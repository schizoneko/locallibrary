import datetime
from urllib import request
from django.shortcuts import render
from django.views import generic, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from .models import Book, Author, BookInstance, Genre
from .constants import (
    LOAN_STATUS,
    NUM_BOOK_VIEW,
    NUM_VISITS,
    NUM_OF_WEEKS_DEFAULT,
    INITIAL_DATE_OF_DEATH,
)
from .forms import RenewBookForm

# Create your views here.

def index(request):
    """View function for home page of site."""
    
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact=LOAN_STATUS.AVAILABLE.value
    ).count()
    
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', NUM_VISITS)
    request.session['num_visits'] = num_visits + NUM_VISITS
    
    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
    }
    
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = NUM_BOOK_VIEW
    context_object_name = "book_list"
    template_name = "catalog/book_list.html"
    queryset = Book.objects.all().order_by("title")


class BookDetailView(generic.DetailView):
    """Generic class-based view for a book detail page."""

    model = Book

    def get_context_data(self, **kwargs):
        """Add additional context data to the view."""
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context["LOAN_STATUS"] = LOAN_STATUS
        context["book_instances"] = self.object.bookinstance_set.all()
        return context

    def book_detail_view(self, primary_key):
        """View function for displaying a book detail page."""
        book = get_object_or_404(Book, pk=primary_key)

        return render(request, "catalog/book_detail.html", context={"book": book})


class LoanedBooksByUserListView(generic.ListView):
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = NUM_BOOK_VIEW

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact=LOAN_STATUS.ON_LOAN.value)
            .order_by("due_back")
        )


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == "POST":
        form = RenewBookForm(request.POST)
    if form.is_valid():
        book_instance.due_back = form.cleaned_data["renewal_date"]
        book_instance.save()
        return HttpResponseRedirect(reverse("all-borrowed"))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(
            weeks=NUM_OF_WEEKS_DEFAULT
        )
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

    context = {"form": form, "book_instance": book_instance}

    return render(request, "catalog/book_renew_librarian.html", context)


@login_required
@require_POST
def borrow_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if book_instance.status != LOAN_STATUS.AVAILABLE.value:
        return redirect("book-detail", pk=book_instance.book.pk)

    book_instance.status = LOAN_STATUS.ON_LOAN.value
    book_instance.borrower = request.user
    book_instance.due_back = datetime.date.today() + datetime.timedelta(
        weeks=NUM_OF_WEEKS_DEFAULT
    )
    book_instance.save()

    return redirect("book-detail", pk=book_instance.book.pk)


class AuthorCreate(CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    initial = {"date_of_death": INITIAL_DATE_OF_DEATH}


class AuthorUpdate(UpdateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy("authors")
