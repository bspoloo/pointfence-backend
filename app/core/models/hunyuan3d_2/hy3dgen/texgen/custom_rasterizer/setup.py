from setuptools import setup, find_packages
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

custom_rasterizer_module = CUDAExtension(
    name='custom_rasterizer_kernel',
    sources=[
        'lib/custom_rasterizer_kernel/rasterizer.cpp',
        'lib/custom_rasterizer_kernel/grid_neighbor.cpp',
        'lib/custom_rasterizer_kernel/rasterizer_gpu.cu',
    ],
    extra_compile_args={
        'cxx': ['/std:c++17'],
        'nvcc': [
            '-allow-unsupported-compiler',
        ],
    },
)

setup(
    name='custom_rasterizer',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    ext_modules=[
        custom_rasterizer_module,
    ],
    cmdclass={
        'build_ext': BuildExtension
    },
)