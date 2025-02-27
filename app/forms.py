from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_countries.fields import CountryField
from django_select2.forms import Select2Widget
from .models import CustomUser, LectureAttendance, Certificate


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    full_name = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    nationality = CountryField().formfield()
    phone_number = forms.CharField(max_length=15)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'gender', 'nationality', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data['full_name']
        first_name, last_name = full_name.split(' ', 1)
        user.first_name = first_name
        user.last_name = last_name
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'gender', 'nationality', 'phone_number')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'gender', 'nationality', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        if commit:
            user.save()
        return user

class LectureAttendanceForm(forms.ModelForm):
    class Meta:
        model = LectureAttendance
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(LectureAttendanceForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('', 'Select status'),  # Add a placeholder option
            ('not_yet', 'Not Yet'),
            ('listening', 'Listening'),
            ('watched', 'Watched')
        ]
        self.fields['status'].widget.attrs['disabled'] = 'disabled'  # Disable the placeholder option

class UserSelect2Widget(Select2Widget):
    search_fields = [
        'id__icontains',
        'username__icontains',
        'full_name__icontains',
    ]
    
class CertificateAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        widget=UserSelect2Widget(attrs={'data-placeholder': 'Search for a user by Username...'}),
        label='User'
    )

    class Meta:
        model = Certificate
        fields = '__all__'
