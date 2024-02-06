from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositeForm, WithdrawForm, LoanRequestForm, TransferBalanceForm
from .constants import DEPOSITE, WITHDRAWAL, LOAN, LOAN_PAID, TRANSFER_BALANCE, RECEIVE_BALANCE
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from accounts.models import UserBankAccount
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user': user,
        'amount': amount,
    })
    to_email = user.email
    send_eamil = EmailMultiAlternatives(subject, ' ', to=[to_email])
    send_eamil.attach_alternative(message, 'text/html')
    send_eamil.send()


class TrasnctionMixinView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    title = ''
    success_url = reverse_lazy('transction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context


class DepositeMoneyView(TrasnctionMixinView):
    form_class = DepositeForm
    title = 'Deposite Money'

    def get_initial(self):
        initial = {'transaction_type': DEPOSITE}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        print(account.balance)
        account.balance += amount
        account.save(
            update_fields=['balance']
        )

        messages.success(
            self.request, f'{amount} $ has been diposit successfully.')
        
        # mail_subject = 'Deposit Message'
        # message = render_to_string('transactions/deposit_send_email.html',{
        #     'user' : self.request.user,
        #     'amount' : amount,
        # })
        # to_email = self.request.user.email
        # send_email = EmailMultiAlternatives(mail_subject, ' ', to=[to_email])
        # send_email.attach_alternative(message, 'text/html')
        # send_email.send()

        send_transaction_email(self.request.user, amount, 'Deposit Balance', 'transactions/deposit_send_email.html')

        return super().form_valid(form)


# class WithdrawalMoneyView(TrasnctionMixinView):
#     form_class = WithdrawForm
#     title = 'Withdrawal Money'

#     def get_initial(self):
#         initial = {'transaction_type': WITHDRAWAL}
#         return initial

#     def form_valid(self, form):
#         rupt = UserBankAccount().objects.get('account')
#         print(rupt.account)
#         if rupt.bankrupt:
#             rupt.bankrupt = True
#             rupt.save()
#             messages.error(self.request, 'This Bank is Rupt Now!')
#         else:
#             amount = form.cleaned_data.get('amount')
#             self.request.user.account.balance -= form.cleaned_data.get('amount')

#             self.request.user.account.save(
#                 update_fields=['balance']
#             )

#             messages.success(
#                 self.request, f'{amount} $ has been withdrawn successfully')
#         return super().form_valid(form)
    
class WithdrawalMoneyView(TrasnctionMixinView):
    form_class = WithdrawForm
    title = 'Withdrawal Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        bank_account = self.request.user.account

        if bank_account.bankrupt:
            messages.error(self.request, 'This Bank is Rupt Now! Please Contact your Admin !')
            send_transaction_email(self.request.user, '', 'BankRupt Now', 'transactions/bankrupt_email.html')
            return redirect('withdraw_money')
        else:
            amount = form.cleaned_data.get('amount')

            if bank_account.balance >= amount:
                bank_account.balance -= amount
                bank_account.save(update_fields=['balance'])

                messages.success(self.request, f'{amount} $ has been withdrawn successfully')

                send_transaction_email(self.request.user, amount, 'Withdraw Balance', 'transactions/withdraw_send_email.html')

            else:
                messages.error(self.request, 'Insufficient balance for withdrawal')

        return super().form_valid(form)

class LoanRequestView(TrasnctionMixinView):
    form_class = LoanRequestForm
    title = 'Loan For Request'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type=LOAN, loan_approved=True).count()
        if current_loan_count >= 2:
            return HttpResponse('You have crossed your limis.')

        messages.success(
            self.request, f'Loan request for amount {amount} $ has been successfully created.')
        
        send_transaction_email(self.request.user, amount, 'Loan Request', 'transactions/loan_request_email.html')
        return super().form_valid(form)


class TransctionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            queryset = queryset.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })
        return context


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        if loan.loan_approved:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                send_transaction_email(self.request.user, loan.amount, 'Loan Pay', 'transactions/loan_pay_email.html')
                return redirect('loan_list')
            else:
                messages.error(
                    self.request, f'Loan balance is gather than your available balance')

        return redirect('loan_list')


class LoanListView(LoginRequiredMixin, ListView):
    template_name = 'transactions/loan_request.html'
    model = Transaction
    context_object_name = 'loans'

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(
            account=user_account, transaction_type=LOAN)
        return queryset


class TransferBalanceView(View):
    template_name = 'transactions/transfer_balance.html'

    def get(self, request):
        form = TransferBalanceForm()
        return render(request, self.template_name,{'form':form, 'title' : 'Transfer Balance'})
    
    def post(self,request):
        form = TransferBalanceForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            receiver_id = form.cleaned_data['receiver_id']

            current_user = request.user.account
            print(current_user.balance ,'###')

            try:
                receiver_user = UserBankAccount.objects.get(account_no = receiver_id)

                current_user.balance -= amount
                current_user.save()

                receiver_user.balance += amount
                receiver_user.save()

                Transaction.objects.create(
                    account = current_user,
                    transaction_type = TRANSFER_BALANCE,
                    amount = amount,
                    balance_after_transaction = current_user.balance
                )
                Transaction.objects.create(
                    account = receiver_user,
                    transaction_type = RECEIVE_BALANCE,
                    amount = amount,
                    balance_after_transaction = receiver_user.balance
                )

                messages.success(request, f'{amount} $ Successfully Sended !')

                send_transaction_email(self.request.user, amount, 'Transfer Balance', 'transactions/transfer_sender_email.html')
                send_transaction_email(receiver_user, amount, 'Transfer Balance', 'transactions/transfer_receiver_email.html')

            except UserBankAccount.DoesNotExist:
                messages.error(request, f'Does not exist')
                return redirect('transfer_balance')

        return redirect('transction_report')