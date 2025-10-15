import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ExpenseForm, CategoryForm
from .models import Expense, Category


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    start_month = today.replace(day=1)

    monthly_total = (
        Expense.objects.filter(user=request.user, date__gte=start_month, date__lte=today)
        .aggregate(total=Sum('amount'))
        .get('total')
        or 0
    )

    by_category = (
        Expense.objects.filter(user=request.user, date__gte=start_month, date__lte=today)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    labels = [(row['category__name'] or 'Uncategorized') for row in by_category]
    data = [float(row['total'] or 0) for row in by_category]

    recent = Expense.objects.filter(user=request.user).order_by('-date', '-created_at')[:10]

    context = {
        'monthly_total': monthly_total,
        'by_category': list(by_category),
        'chart_labels_json': json.dumps(labels),
        'chart_data_json': json.dumps(data),
        'recent': recent,
    }
    return render(request, 'expenses/dashboard.html', context)


@login_required
def expense_list(request: HttpRequest) -> HttpResponse:
    expenses = Expense.objects.filter(user=request.user).order_by('-date', '-created_at')
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})


@login_required
def expense_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense: Expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form})


@login_required
def expense_update(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form})


@login_required
def expense_delete(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


@login_required
def category_list(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'expenses/category_list.html', {'categories': categories})


@login_required
def category_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category: Category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'expenses/category_form.html', {'form': form})


@login_required
def category_update(request: HttpRequest, pk: int) -> HttpResponse:
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'expenses/category_form.html', {'form': form})


@login_required
def category_delete(request: HttpRequest, pk: int) -> HttpResponse:
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'expenses/category_confirm_delete.html', {'category': category})
