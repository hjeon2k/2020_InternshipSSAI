def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.mp4', '.mov', '.avi']
    limit = 510*1024*1024
    if value.size > limit:
        raise ValidationError('File size should not exceed 500MB.')
    if not ext.lower() in valid_extensions:
        raise ValidationError('Only .mp4 .mov .avi are accepted')
