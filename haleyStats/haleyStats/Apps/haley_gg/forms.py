from django import forms

from .Models.maps import Map


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ('name', 'file', 'image')

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False
