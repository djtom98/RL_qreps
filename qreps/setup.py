"""Setup script for qreps."""
from setuptools import find_packages, setup

extras = {
    "test": [
        "pytest>=5.0,<5.1",
        "flake8>=3.7.8,<3.8",
        "pydocstyle==4.0.0",
        "black>=19.10b0",
        "isort>=5.0.0",
        "pytest_cov>=2.7,<3",
        "mypy==0.750",
        "pre-commit",
    ],
    "logging": ["tensorboard>=2.0,<3"],
    "experiments": ["lsf_runner==0.0.5", "pandas==0.25.0", "dotmap>=1.3.0,<1.4.0"],
}

setup(
    name="qreps",
    version="0.0.1",
    author="Sebastian Curi",
    author_email="sebascuri@gmail.com",
    license="MIT",
    packages=find_packages(exclude=["docs"]),
    install_requires=[
        # "rllib @ git+ssh://git@github.com/sebascuri/rllib@master#egg=rllib",
        # "rllib @ git+ssh://git@github.com/sebascuri/rllib@16fd88914ab35b775839423bdca0f491a34cc612#egg=rllib",
        "numpy>=1.14,<2",
        "scipy>=1.3.0,<1.4.0",
        "torch>=1.5.0,<1.7.0",
        "gym>=0.15.4",
        "atari_py>=0.2.6",
        "tqdm>=4.0.0,<5.0",
        "matplotlib>=3.1.0",
        "tensorboardX>=2.0,<3",
    ],
    extras_require=extras,
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)


# commit 021faab6b8dd0a06df82e651b089fada40e53680
# Author: Lukas Froehlich <lukasfro@ethz.ch>
# Date:   Thu Mar 18 13:24:22 2021 +0100

#     Fix set_state for Gym/VectorizedEnv

# commit 31094d3a5130932e770ec583898ab68c487efb55
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:05:05 2021 +0100

#     Add argument flag to run with tensorboard

# commit 103e9779971ed1d04177ba91f62d02863127b7a6
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:04:24 2021 +0100

#     Refactor MPO and detach gradients after parenthesis to be sure there is no leaking

# commit 18d9f2e6e9b342cc816c3bc39db4ba3ddc275cf1
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:03:48 2021 +0100


# commit 18d9f2e6e9b342cc816c3bc39db4ba3ddc275cf1
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:03:48 2021 +0100

#     Add Lagrangian loss to init

# commit da1186f080cf581eed181a2a81fc50bf0d254944
# commit da1186f080cf581eed181a2a81fc50bf0d254944
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:03:30 2021 +0100

#     Add Lagrangian loss to init

# commit da1186f080cf581eed181a2a81fc50bf0d254944
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:03:30 2021 +0100

#     Refactor REPS and REPSAgent files



# commit 103e9779971ed1d04177ba91f62d02863127b7a6
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:04:24 2021 +0100

#     Refactor MPO and detach gradients after parenthesis to be sure there is no leaking

# commit 18d9f2e6e9b342cc816c3bc39db4ba3ddc275cf1
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:03:48 2021 +0100


# commit 18d9f2e6e9b342cc816c3bc39db4ba3ddc275cf1
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:03:48 2021 +0100

#     Add Lagrangian loss to init

# commit da1186f080cf581eed181a2a81fc50bf0d254944
# commit da1186f080cf581eed181a2a81fc50bf0d254944
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:03:30 2021 +0100

#     Add Lagrangian loss to init

# commit da1186f080cf581eed181a2a81fc50bf0d254944
# Author: scuri <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 13:03:30 2021 +0100

#     Refactor REPS and REPSAgent files

# commit 16fd88914ab35b775839423bdca0f491a34cc612
# Merge: a00052a bf3eb0a
# Author: Sebastian Curi <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 12:37:28 2021 +0100

#     Merge pull request #4 from sebimarkgraf/fix/reps-weights
    
#     Change weights of NLL in reps to include exponential


#     Refactor REPS and REPSAgent files

# commit 16fd88914ab35b775839423bdca0f491a34cc612
# Merge: a00052a bf3eb0a
# Author: Sebastian Curi <sebastian.curi@inf.ethz.ch>
# Date:   Thu Mar 18 12:37:28 2021 +0100
