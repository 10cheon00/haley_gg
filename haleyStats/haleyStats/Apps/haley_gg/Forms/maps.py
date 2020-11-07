from django import forms

from ..Models.maps import Map


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