# 遮标

## 环境

Python 3.11.3 (main, Apr 19 2023, 23:54:32) [GCC 11.2.0] on linux

下载 pyzbar opencv-python moviepy 包即可，以防版本问题，另附pip freeze

asttokens @ file:///home/conda/feedstock_root/build_artifacts/asttokens_1670263926556/work
autopep8==2.0.2
backcall @ file:///home/conda/feedstock_root/build_artifacts/backcall_1592338393461/work
backports.functools-lru-cache @ file:///home/conda/feedstock_root/build_artifacts/backports.functools_lru_cache_1618230623929/work
certifi==2023.5.7
charset-normalizer==3.1.0
debugpy @ file:///work/ci_py311/debugpy_1676824903649/work
decorator==4.4.2
executing @ file:///home/conda/feedstock_root/build_artifacts/executing_1667317341051/work
idna==3.4
imageio==2.31.1
imageio-ffmpeg==0.4.8
importlib-metadata @ file:///home/conda/feedstock_root/build_artifacts/importlib-metadata_1682176699712/work
ipykernel @ file:///home/conda/feedstock_root/build_artifacts/ipykernel_1655369107642/work
ipython @ file:///home/conda/feedstock_root/build_artifacts/ipython_1685727741709/work
jedi @ file:///home/conda/feedstock_root/build_artifacts/jedi_1669134318875/work
jupyter_client @ file:///home/conda/feedstock_root/build_artifacts/jupyter_client_1681432441054/work
jupyter_core @ file:///home/conda/feedstock_root/build_artifacts/jupyter_core_1678994187655/work
matplotlib-inline @ file:///home/conda/feedstock_root/build_artifacts/matplotlib-inline_1660814786464/work
moviepy==1.0.3
nest-asyncio @ file:///home/conda/feedstock_root/build_artifacts/nest-asyncio_1664684991461/work
numpy==1.24.3
opencv-python==4.7.0.72
packaging @ file:///home/conda/feedstock_root/build_artifacts/packaging_1681337016113/work
parso @ file:///home/conda/feedstock_root/build_artifacts/parso_1638334955874/work
pexpect @ file:///home/conda/feedstock_root/build_artifacts/pexpect_1667297516076/work
pickleshare @ file:///home/conda/feedstock_root/build_artifacts/pickleshare_1602536217715/work
Pillow==9.5.0
platformdirs @ file:///home/conda/feedstock_root/build_artifacts/platformdirs_1686403120743/work
proglog==0.1.10
prompt-toolkit @ file:///home/conda/feedstock_root/build_artifacts/prompt-toolkit_1677600924538/work
psutil @ file:///work/ci_py311_2/psutil_1679337388738/work
ptyprocess @ file:///home/conda/feedstock_root/build_artifacts/ptyprocess_1609419310487/work/dist/ptyprocess-0.7.0-py2.py3-none-any.whl
pure-eval @ file:///home/conda/feedstock_root/build_artifacts/pure_eval_1642875951954/work
pycodestyle==2.10.0
Pygments @ file:///home/conda/feedstock_root/build_artifacts/pygments_1681904169130/work
PyPatchMatch==1.0.0
python-dateutil @ file:///home/conda/feedstock_root/build_artifacts/python-dateutil_1626286286081/work
pyzbar==0.1.9
pyzmq @ file:///croot/pyzmq_1686601365461/work
requests==2.31.0
six @ file:///home/conda/feedstock_root/build_artifacts/six_1620240208055/work
stack-data @ file:///home/conda/feedstock_root/build_artifacts/stack_data_1669632077133/work
tornado @ file:///work/ci_py311/tornado_1676823418767/work
tqdm==4.65.0
traitlets @ file:///home/conda/feedstock_root/build_artifacts/traitlets_1675110562325/work
typing_extensions @ file:///home/conda/feedstock_root/build_artifacts/typing_extensions_1685704949284/work
urllib3==2.0.3
wcwidth @ file:///home/conda/feedstock_root/build_artifacts/wcwidth_1673864653149/work
zipp @ file:///home/conda/feedstock_root/build_artifacts/zipp_1677313463193/work

## config 参数

* query
    * path 查询png图像路径
    * min_match 最小命中数，默认 5
    * knn_ratio 最近搜索限制比例，默认 0.5
    * min_similarity 最小图像颜色相似度，默认 None
    * min_scale 最小放缩比例，默认 None
    * min_scale 最大放缩比例，默认 None
    * min_translation 最大平移，默认 None
    * min_rotation 最大旋转，默认 None
    * pre_frame_num 移除提前帧数, 默认 0
    * post_frame_num 移除延后帧数, 默认 0
* remove
    * strategy COVER 或 INPAINT 默认值为 INPAINT
    * path COVER 的遮盖png图像路径