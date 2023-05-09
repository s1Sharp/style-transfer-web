from enum import Enum

from torch_model import StyleTransferNet
from database import s3storage

s3_proxy = s3storage.s3_proxy
net = StyleTransferNet(s3_proxy)

# to import
StyleNamesDict = [(model_name, model_name) for model_name in net.models.keys()]
StyleNames = Enum('StyleNames', dict(StyleNamesDict))


def get_style_name(style_name: StyleNames):
    return style_name.value
