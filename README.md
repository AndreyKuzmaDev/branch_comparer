# branch comparer
Branch comparer is a simple tool to track states of packages in sisyphus and p11 repositories. You can check wich packages are present only in one of them and wich are present in both but have most recent version only in one
# Instalation
Download binaries from latest release and run 
``` 
pip3 install ARCHIVE_NAME.tar.gz
```
WARNING: you may need to add ```/home/USERNAME/.local/bin``` directory to $PATH to be able to run script from any directory
# Usage

```
compare-branches [OPTIONS] [OUT_PATH]                                   

Parameters:
out_path      [OUT_PATH]  Path to output file [default: comparison.json]

Options:
--arch TEXT  Find only packages with specific architecture (x86_64, aarch64, i586, noarch, x86_64-i586)
--find-sisyphus-only / --no-find-sisyphus-only  Find packages that present only in sisyphus
--find-p11-only / --no-find-p11-only  Find packages that present only in p11
--find-sisyphus-outdated / --no-find-sisyphus_outdated  Find packages that have more recent version in p11
--find-p11-outdated / --no-find-p11-outdated  Find packages that have more recent version in sisyphus
--detailed -d  Write to file detailed info about packages (default - just names)
--use-release -r  Use release number instead of version number to detect outdated packages
--verbose -v  Print info about progress
--help Show this message and exit
```

# Output

Output is .json file with varying structure

Without parameters:
```json
{
  "arch" : {
    "sisyphus_only" : [
      "string"
    ],
    "p11_only" : [
      "string"
    ],
    "sisyphus_outdated" : [
      "string"
    ],
    "p11_outdated" : [
      "string"
    ]
  }
}
```

With specified architecture:
```json
{
  "sisyphus_only" : [
    "string"
  ],
  "p11_only" : [
    "string"
  ],
  "sisyphus_outdated" : [
    "string"
  ],
  "p11_outdated" : [
    "string"
  ]
}
```

With ```--detailed``` flag:
```json
{
  "arch" : {
    "sisyphus_only" : {
      "name" : {
        "name": "string",
        "epoch": 0,
        "version": "string",
        "release": "string",
        "arch": "string",
        "disttag": "string",
        "buildtime": 0,
        "source": "string"
      }
    },
    "p11_only" : {
      "name" : {
        "name": "string",
        "epoch": 0,
        "version": "string",
        "release": "string",
        "arch": "string",
        "disttag": "string",
        "buildtime": 0,
        "source": "string"
      }
    },
    "sisyphus_outdated" : {
      "name" : {
        "name": "string",
        "epoch": 0,
        "version": "string",
        "release": "string",
        "arch": "string",
        "disttag": "string",
        "buildtime": 0,
        "source": "string",
        "latest_version": "string",
        "latest_release": "string"
      }
    },
    "p11_outdated" : {
      "name" : {
        "name": "string",
        "epoch": 0,
        "version": "string",
        "release": "string",
        "arch": "string",
        "disttag": "string",
        "buildtime": 0,
        "source": "string",
        "latest_version": "string",
        "latest_release": "string"
      }
    }
  }
}
```

