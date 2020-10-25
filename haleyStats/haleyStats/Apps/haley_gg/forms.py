from django import forms

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

    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        # Add fields 'player_1, 2' and 'is_player_1_winner'.
        # For now, I can't make searching user query.
        # So replaced by a ModelChoiceField.
        self.fields['player_1'] = forms.ModelChoiceField(
            queryset=User.objects.all(), empty_label=None)
        self.fields['player_2'] = forms.ModelChoiceField(
            queryset=User.objects.all(), empty_label=None)
        self.fields['is_player_1_winner'] = forms.BooleanField(required=False)

    def clean(self):
        super(MatchForm, self).clean()
        data = self.cleaned_data
        # 1. Check reduplication on rounds and set.
        if Match.objects.filter(name=data['name'], set=data['set']).exists():
            error_msg = u"Already exist match. Check match name or set."
            self.add_error('set', error_msg)

        # 2. Check same user on fields.
        if data['player_1'] == data['player_2']:
            error_msg = u"Players should not same."
            self.add_error('player_1', error_msg)
        return data

    def save(self, commit=True):
        data = super(MatchForm, self).save(commit=False)
        if commit:
            # First, Create Match model.
            data.save()

            # Secondly, Add match count plus 1 on map.
            self.cleaned_data['map'].add_count(1)

            # Thirdly, Create Player model related Match model.
            p1 = Player.objects.create(
                user=self.cleaned_data['player_1'],
                match=data)
            p2 = Player.objects.create(
                user=self.cleaned_data['player_2'],
                match=data)

            # Fourthly, Save who is winner in data.
            if self.cleaned_data['is_player_1_winner']:
                p1.is_win = True
                p1.save()
            else:
                p2.is_win = True
                p2.save()

        return data
