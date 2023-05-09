import os
import io
import enum
from typing import BinaryIO, List, Optional, Tuple, Union

import torch
from PIL import Image
from torchvision.utils import save_image, make_grid

from nn_model.nn import (
    TransformerNet, 
    style_transform,
    custom_denormalize,
)

from task.bucket_utils import S3StorageProxy


# style-bucket
# torch_models
# style_transfer
# v1
class StyleTransferNet():
    def __init__(self,
            s3proxy: S3StorageProxy,
            bucket_name: str = 'style-bucket',
            models_version: str = "v1",
            enable_model_caching: bool = True,
            image_size: int = 512,
        ):
        self.s3 = s3proxy
        self.bucket_name = bucket_name
        self.models_s3_path = f"torch_models/style_transfer/{models_version}/"
        self.model_caching = enable_model_caching
        self.models = dict()
        self.device = torch.device( "cpu" )
        self.image_size = image_size

        s3_model_names = self.s3.list_object_keys_by_filter(prefix=self.models_s3_path, endwith=".pth")
        for model in s3_model_names:
            local_model_path, style_model_name = self.download_model(model)
            if local_model_path is not None:
                transformer = TransformerNet().to(self.device)
                transformer.load_state_dict(torch.load(local_model_path, map_location=self.device))
                self.models[style_model_name] = transformer
        print(f"style_model_name keys {self.models.keys()}")


    def download_model(self, model_path) -> Optional[Tuple[str]]:
        model_name = model_path.split("/")[-1]
        style_name = model_name.split(".")[0]
        if self.model_caching:
            cache_path = f"/tmp/{model_name}"
            print(f"caching in {cache_path} path")
            try:
                if os.path.isfile(cache_path) and os.access(cache_path, os.R_OK):
                    print(f"File {cache_path} exists and is readable")
                    return cache_path, style_name
                else:
                    self.s3.download_file(key_name=model_path, local_path=cache_path)
                    print("Either the file is missing or not readable")
                    return cache_path, style_name

            except Exception as e:
                print(f"error happend while downloading {model_path} error is {e}")
                return None


    def create_image_test(self, file: bytes, model_name: str = 'starry_night'):
        image = Image.open(io.BytesIO(file))
        image_samples = [style_transform(self.image_size)(image)]
        image_samples = torch.stack(image_samples)

        transformer = self.models[model_name]

        transformer.eval()
        with torch.no_grad():
            output = transformer(image_samples.to(self.device))
        image_grid = custom_denormalize(output.cpu())

        # save_image(image_grid, f"/home/home/images/outputs/starry_night-training/test.jpg")
        output_binary = self.pathed_get_image_bytes(image_grid)

        return output_binary

        # os.makedirs("/home/home/images/outputs/starry_night-training/", exist_ok=True)
        # save_image(image_grid, f"/home/home/images/outputs/starry_night-training/test.jpg")
        # return "/home/home/images/outputs/starry_night-training/test.jpg"


    def pathed_get_image_bytes(
        self,
        tensor: Union[torch.Tensor, List[torch.Tensor]],
        **kwargs,
    ) -> bytes:
        grid = make_grid(tensor, **kwargs)
        # Add 0.5 after unnormalizing to [0, 255] to round to nearest integer
        ndarr = grid.mul(255).add_(0.5).clamp_(0, 255).permute(1, 2, 0).to("cpu", torch.uint8).numpy()
        im = Image.fromarray(ndarr)
        # BytesIO is a file-like buffer stored in memory
        img_byte_arr = io.BytesIO()
        # image.save expects a file-like as a argument
        im.save(img_byte_arr, format='JPEG') # im.format)
        # Turn the BytesIO object back into a bytes object
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr


if __name__=='__main__':
    import os
    import sys
    import random

    sys.path.append(os.path.join(sys.path[0], '/home/web'))
    with open("/home/src/styles/mosaic.jpg", "rb") as file:
        net = StyleTransferNet()
        net.create_image_test(file.read())

    # models_data = {}
    
    # image_size = 256
    # dataset_path = "/home/train/train_dataset"
    # checkpoint_model_path = "/home/web/web_app/torch_models/starry_night_20000.pth"
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # transformer = TransformerNet().to(device)
    # transformer.load_state_dict(torch.load(checkpoint_model_path, map_location=device))

    # image_samples = []
    # for path in random.sample(glob.glob(f"{dataset_path}/*/*.jpg"), 8):
    #     image_samples += [style_transform(image_size)(Image.open(path))]
    # image_samples = torch.stack(image_samples)
    # transformer.eval()
    # with torch.no_grad():
    #     output = transformer(image_samples.to(device))
    # image_grid = custom_denormalize(torch.cat((image_samples.cpu(), output.cpu()), 2))
    # os.makedirs("home/images/outputs/starry_night-training/", exist_ok=True)
    # save_image(image_grid, f"home/images/outputs/starry_night-training/test.jpg", nrow=4)
