# haley_gg/forms.py
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import User
from .models import Match
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
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }),
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }),
            'most_race': forms.Select(
                attrs={
                    'class': 'form-control'
                })
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
class UpdateUserForm(CreateUserForm):
    class Meta(CreateUserForm.Meta):
        # Show all field in User model.
        fields = CreateUserForm.Meta.fields + [
            'career'
        ]
        CreateUserForm.Meta.widgets.update({
            'career': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }),
        })

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

    class Meta:
        model = Map
        fields = [
            'name',
            'file',
            'image'
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }),
            'file': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'type': 'file',
                }),
            'image': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'type': 'file',
                })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['file'].required = True
        # self.fields['image'].required = True

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
        required=False)

    def clean_user_name(self):
        user_name = self.cleaned_data['user_name']
        if user_name == "":
            msg = u"이름을 입력해주세요."
            self.add_error('user_name', msg)
        return user_name


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'date',
            'league',
            'map',
            'round',
            'group',
            'set',
            'remark'
        ]
        widgets = {
            'date': forms.NumberInput(
                attrs={'type': 'date'}),
        }


class OneOnOneMatchForm(MatchForm):
    race_list = (
        ('T', 'Terran'),
        ('Z', 'Zerg'),
        ('P', 'Protoss'),
    )

    class Meta(MatchForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['player_A'] = forms.CharField(
            validators=[search_user])
        self.fields['player_B'] = forms.CharField(
            validators=[search_user])
        self.fields['player_A_race'] = forms.ChoiceField(
            choices=self.race_list)
        self.fields['player_B_race'] = forms.ChoiceField(
            choices=self.race_list)

    def clean(self):
        super().clean()
        player_a = self.cleaned_data['player_A']
        player_b = self.cleaned_data['player_B']
        if player_a != player_b:
            error_msg = u"Same user name doesn't allowed."
            self.add_error('player_a', error_msg)

    def save(self):
        super().save()


class TopAndBottomMatchForm(MatchForm):
    class Meta(MatchForm.Meta):
        widgets = {
            # 'A_team_is_win': forms.
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 4):
            self.fields['A Team player ' + str(i)] = forms.CharField(
                validators=[search_user],
                label='A팀 플레이어 ' + str(i))
        for i in range(1, 4):
            self.fields['B Team player ' + str(i)] = forms.CharField(
                validators=[search_user],
                label='B팀 플레이어 ' + str(i))
        self.fields['A_team_is_win'] = forms.BooleanField()

    def clean(self):
        super().clean()
