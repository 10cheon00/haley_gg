# haley_gg/forms.py
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import User
from .models import Map
from .validator import load_document
from .validator import search_user


# Create User model but not provide 'career' field.
class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'name',
            'joined_date',
            'most_race'
        ]
        widgets = {
            'joined_date': forms.NumberInput(
                attrs={'type': 'date'}),
        }

    # Check that the user name is already exist.
    def clean_name(self):
        name = self.cleaned_data['name']
        if name == 'new':
            error_msg = u"This name cannot allowed."
            self.add_error('name', error_msg)

        try:
            if User.objects.get(name__iexact=name):
                error_msg = u"Already exist user name."
                self.add_error('name', error_msg)
        except ObjectDoesNotExist:
            pass
        return name


# Update User model. Provide all field.
class UpdateUserForm(forms.ModelForm):
    class Meta:
        # Show all field in User model.
        model = User
        fields = [
            'name',
            'joined_date',
            'most_race',
            'career'
        ]
        widgets = {
            'joined_date': forms.NumberInput(
                attrs={'type': 'date'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']

        if name == 'new':
            error_msg = u"This name cannot allowed."
            self.add_error('name', error_msg)

        try:
            exist_user = User.objects.get(name__iexact=name)
            if exist_user:
                # 자기 이름인데 대소문자만 변경하는 경우를 검사한다.
                if exist_user.name.lower() != name.lower():
                    error_msg = u"Already exist user."
                    self.add_error('name', error_msg)
        except ObjectDoesNotExist:
            pass
        return name


# Map form.
class CreateMapForm(forms.ModelForm):
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
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True
        self.fields['image'].required = True

    # Check that the map name is already exist.
    def clean_name(self):
        name = self.cleaned_data['name']
        if name == 'new':
            error_msg = u"This name cannot allowed."
            self.add_error('name', error_msg)

        try:
            if Map.objects.get(name__iexact=name):
                error_msg = u"Already exist map name."
                self.add_error('name', error_msg)
        except ObjectDoesNotExist:
            pass
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


class UpdateMapForm(CreateMapForm):
    class Meta(CreateMapForm.Meta):
        pass

    def clean_name(self):
        name = self.cleaned_data['name']

        if name == 'new':
            error_msg = u"This name cannot allowed."
            self.add_error('name', error_msg)

        try:
            exist_user = User.objects.get(name__iexact=name)
            if exist_user:
                # 자기 이름인데 대소문자만 변경하는 경우를 검사한다.
                if exist_user.name.lower() != name.lower():
                    error_msg = u"Already exist user."
                    self.add_error('name', error_msg)
        except ObjectDoesNotExist:
            pass
        return name


class MatchSheetForm(forms.Form):
    document_url = forms.URLField(
        label="데이터 스프레드시트 URL",
        validators=[load_document])


class CompareForm(forms.Form):
    user_1 = forms.CharField(
        label="유저명",
        validators=[search_user],
        required=True)

    user_2 = forms.CharField(
        label="유저명",
        validators=[search_user],
        required=True)

    # Leave map filter to frontend...
    # map_name = forms.CharField(
    #     label="맵",
    #     required=False)

    # def clean_map(self):
    #     map_name = self.cleaned_data['map_name']
    #     if map_name == "":
    #         return map_name
    #     try:
    #         Map.objects.get(name__iexact=map_name)
    #     except ObjectDoesNotExist:
    #         error_msg = u"This map is not exist."
    #         self.add_error('map', error_msg)
    #     return map_name


class SearchUserForm(forms.Form):
    user_name = forms.CharField(
        label="유저명",
        validators=[search_user],
        required=True)
