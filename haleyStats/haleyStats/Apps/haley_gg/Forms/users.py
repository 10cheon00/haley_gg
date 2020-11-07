from django import forms

from ..Models.users import User


# Create User model but not provide 'career' field.
class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'name',
            'joined_date',
            'most_race'
        ]

    # Check that the user name is already exist.
    def clean_name(self):
        name = self.cleaned_data['name']
        if User.objects.filter(name__iexact=name):
            error_msg = u"Already exist user name."
            self.add_error('name', error_msg)
        if name == 'new':
            error_msg = u"This name cannot allowed."
            self.add_error('name', error_msg)
        return name


# Update User model. Provide all field.
class UpdateUserForm(CreateUserForm):
    class Meta(CreateUserForm.Meta):
        # Show all field in User model.
        fields = [
            'name',
            'joined_date',
            'most_race',
            'career'
        ]
