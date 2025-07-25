from django.db import models
from datetime import date
from django.urls import reverse
from django.utils.translation import gettext
from django.contrib.auth.models import User
import uuid
from .constants import (
    MAX_LENGTH_IMPRINT,
    MAX_LENGTH_ISBN,
    MAX_LENGTH_NAME,
    MAX_LENGTH_SUMMARY,
    MAX_LENGTH_TITLE,
    MAX_LENGTH_STATUS,
    LOAN_STATUS,
)

# Create your models here.

class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(
        max_length=MAX_LENGTH_TITLE, 
        help_text=gettext('Enter a book genre (e.g.Science Fiction)'),
    )
    
    def __str__(self):
        """String for representing the Model object."""
        return self.name
    
class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=MAX_LENGTH_TITLE)

    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(
        max_length=MAX_LENGTH_SUMMARY, 
        help_text=gettext('Enter a brief description of the book'),
    )

    isbn = models.CharField(
        'ISBN', 
        max_length=MAX_LENGTH_ISBN, 
        unique=True,
        help_text=gettext(
            '13 Character <ahref="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'
        ),
    )
    
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    
    def __str__(self):
        """String for representing the Model object."""
        return self.title
    
    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])
    
    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ", ".join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = "Genre"

class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        help_text=gettext(
            "Unique ID for this particular book across whole library"),
    )
    book = models.ForeignKey('Book', on_delete=models.RESTRICT)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    borrower = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=MAX_LENGTH_STATUS,
        choices=[
            (tag.value, tag.name.replace("_", " ").title()) for tag in LOAN_STATUS
        ],
        blank=True,
        default=LOAN_STATUS.MAINTENANCE.value,
        help_text=gettext('Book availability'),
    )
    
    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)
        
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'
    
    @property
    def is_overdue(self):
        return self.due_back and date.today() > self.due_back

    
class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=MAX_LENGTH_NAME)
    last_name = models.CharField(max_length=MAX_LENGTH_NAME)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        
    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])
    
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
