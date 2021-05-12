# Copyright 2021 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
# or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Ref: https://stackoverflow.com/questions/60430277/how-to-load-images-from-url-with-a-tensorflow-2-dataset
Ref2: https://www.tensorflow.org/tutorials/load_data/images
"""

import time
from typing import Any, Callable, Dict
import tensorflow as tf
import numpy as np
import cv2
from urllib.request import urlopen
import matplotlib.pyplot as plt
import pandas as pd

def load_data_from_url(data: pd.DataFrame, delay: int = 3, imagedim: int = 224) -> Dict[str, Any]:
    """Loads images from URLs in the csv

    The Partitioned dataset expects a Dict in the following format
    {'filename1': data1, 'filename2: data2}

    Args:
        data (pd.DataFrame): The data has the following fields id, url and labels. labels are seperated by  |
        delay (int, optional): [description]. Defaults to 3.
        imagedim (int, optional): [description]. Defaults to 224.

    Returns:
        Dict[str, Any]: Returns a dict for PartitionedDataset. see the format above
    """
    to_return = {}  # {'filename1': data1, 'filename2: data2} for PartitionedDataset
    for index, row in data.iterrows():
        downloaded_data = read_url(row['url'], delay, imagedim)
        # Example: _dog_black_white_1
        filename = "_" + row['labels'].replace('|', '_') + "_" + str(index)
        to_return[filename] = downloaded_data
    return to_return


def read_url(url: str, delay, imagedim) -> np.ndarray:
    """Loads resizes and returns an image from a URL

    Args:
        url (str): the image Url
        delay (int): Delay between each call.
        imagedim (int): Image dimension

    Returns:
        np.ndarray: [description]
    """
    with urlopen(url) as request:
        time.sleep(delay)
        img_array = np.asarray(bytearray(request.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        res = cv2.resize(img, dsize=(imagedim, imagedim), interpolation=cv2.INTER_CUBIC)
        return cv2.cvtColor(res, cv2.COLOR_BGR2RGB)


def load_data_from_patitioned_dataset(partitioned_input: Dict[str, Callable[[], Any]]) -> Dict[str, Any]:
    """Loads images and labels (from filename eg. _cat_white_tan_12.jpg) from a PartitionedDataset

    Returns
    {
        filename:{
                image: np.array
                labels: List
        }
    }

    Args:
        partitioned_input (Dict[str, Callable[[], Any]]): [description]

    Returns:
        Dict[str, Any]: see the Format above
    """
    to_return = {}
    for partition_key, partition_load_func in sorted(partitioned_input.items()):
        result = {}
    # load the actual partition data which is an np.array preprocessed by tf
        partition_data = partition_load_func()
        labels = partition_key.split('_')[1:-1]
        result['image'] = partition_data
        result['labels'] = labels
        to_return[partition_key] = result
    return to_return
