from django import forms

from .models import User
from .models import Map
from .models import Match


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


# Map form.
class MapForm(forms.ModelForm):
    permissible_map_extensions_list = (
        '.scm',
        '.scx',
    )

    permissible_image_extensions_list = (
        '.png',
        '.jpeg',
        '.jpg',
        '.bmp',
    )

    class Meta:
        model = Map
        fields = ('name', 'file', 'image')

    def __init__(self, *args, **kwargs):
        super(MapForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = True
        self.fields['image'].required = True

    # Check that the map name is already exist.
    def clean_name(self):
        name = self.cleaned_data['name']
        if Map.objects.filter(name__iexact=name):
            error_msg = u"Already exist map name."
            self.add_error('name', error_msg)
        if name == 'new':
            error_msg = u"This name cannot allowed."
            self.add_error('name', error_msg)
        return name

    # Check file extension.
    def clean_file(self):
        map_file = self.cleaned_data['file']

        if map_file:
            file_name = map_file.name
            if file_name.endswith(self.permissible_map_extensions_list):
                pass
            else:
                error_msg = u"This file isn't a map file. Can not allowed."
                self.add_error('file', error_msg)
        return map_file

    # Check image extension.
    def clean_image(self):
        image_file = self.cleaned_data['image']

        if image_file:
            image_name = image_file.name
            if image_name.endswith(self.permissible_image_extensions_list):
                pass
            else:
                error_msg = u"This file isn't an image file. Can not allowed."
                self.add_error('image', error_msg)
        return image_file


# Match form
class CreateMatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'date',
            'league',
            'name',
            'description',
            'remark',
        ]

    def clean(self):
        cleaned_data = super(CreateMatchForm, self).clean()
        if self.errors:
            return cleaned_data
        # Check reduplication on rounds and set.
        if Match.objects.filter(name=cleaned_data['name'],
                                description=cleaned_data['description']
                                ).exists():
            error_msg = u"Already exist match. Check match name or set."
            self.add_error('description', error_msg)
        return cleaned_data

    def save(self, commit=True, **kwargs):
        instance = super(CreateMatchForm, self).save(commit=False)

        if kwargs:
            instance.match_type = kwargs['match-type']
        if commit:
            instance.save()

# 다시 playerformset으로?
