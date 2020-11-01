from django import forms
from django.forms import inlineformset_factory


from .Models.maps import Map
from .Models.stats import Match
from .Models.users import User
from .Models.stats import Player


# Create User model but not provide 'career' field.
class UserCreateForm(forms.ModelForm):
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
class UserUpdateForm(UserCreateForm):
    class Meta(UserCreateForm.Meta):
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


# Match form.
class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'date',
            'league_name',
            'name',
            'set',
            'map',
        ]

    def clean(self):
        cleaned_data = super(MatchForm, self).clean()
        if self.errors:
            return cleaned_data
        # Check reduplication on rounds and set.
        if Match.objects.filter(name=cleaned_data['name'],
                                set=cleaned_data['set']).exists():
            error_msg = u"Already exist match. Check match name or set."
            self.add_error('set', error_msg)
        return cleaned_data


# Model has a foreign key, it is better to use inlineformset.
class PlayerFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super(PlayerFormSet, self).clean()
        users = []
        # check name in player list.
        for form in self.forms:
            user = form.cleaned_data.get('user')
            if user in users:
                error_msg = u"Players should not same."
                form.add_error('user', error_msg)
            else:
                users.append(user)
        return


player_formset_factory = inlineformset_factory(
    parent_model=Match,
    model=Player,
    fields=[
        'user',
        'is_win',
        'race'
    ],
    formset=PlayerFormSet,
    extra=8,  # maximum of forms
    max_num=2,  # maximum of generatable forms
    can_delete=False)  # formset purpose is to delete item
