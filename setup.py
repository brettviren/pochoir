import setuptools

ver_globals = {}
with open("pochoir/version.py") as fp:
    exec(fp.read(), ver_globals)
version = ver_globals["version"]

setuptools.setup(
    name="pochoir",
    version=version,
    author="Brett Viren",
    author_email="brett.viren@gmail.com",
    description="Calculate response functions with FDM field calculations",
    url="https://brettviren.github.io/pochoir",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    install_requires=[
        "click",         # CLI
        "numpy",         # .npz, need numpy in general
    ],
    extras_require={
        "hdf5":"h5py",          # support HDF5 files or
        "plots":"matplotlib",
        "torch":[
            "torch",         # for CPU/GPU
            "torchdiffeq",   # torch rk
        ],
        "cupy":"cupy",
        "numba":"numba",
        "vtk":[
            "pyevtk",        # for optional export to VTK
            "pytest",
        ]
    },
    entry_points = dict(
        console_scripts = [
            'pochoir = pochoir.__main__:main',
        ]
    ),
    #include_package_data=True,
)

