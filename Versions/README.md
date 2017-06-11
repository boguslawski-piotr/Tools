# Versions

A simple but powerful tool that can easily manage application(s) or libraries versions. 

The program was created for .NET and Xamarin platforms, where versions in various formats are typed in many places and it is usually difficult to catch up and remember where and what to change.

But I do not see any reason why this program could not be used in completely different projects for example in Java, Python or Go.

### Usage:

```
Versions [NUMBER] [OPERATION] FILE ...

where:
  NUMBER can be one of:
    --major, --minor, --build, --revision (default)
  OPERATION can be one of:
    --inc (default), --dec
    --set value, --add value, --sub value
  and FILE is a simple json file with detailed
  definition of what and how will be processed.
```

### Examples:

```
Versions --minor FILE
```
Increments (adds 1) minor version numbers whose definitions are written in FILE.

```
Versions --build --add 2 FILE1 FILE2
```

Adds 2 to build numbers whose definitions are written in FILE1 and FILE2.

```
Versions --revision --inc FILE1 --build --set 23 FILE2
```

Increments revision numbers (taking definitions from FILE1) and sets build numbers to 23 (taking definitions from FILE2).

### Sample json file with definitions:

```json
[
  {
    "FileNames": [
      "iOS/Info.plist",
      "macOS/Info.plist"
    ],
    "Entries": [
      {
        "Pattern": "<key>CFBundleShortVersionString</key>\\s*<string>\\s*([0-9]+)\\.([0-9]+)\\.([0-9]+)\\s*</string>",
        "RevisionGroup": -1
      },
      {
        "Pattern": "<key>CFBundleVersion</key>\\s*<string>\\s*([0-9]+)\\.([0-9]+)\\.([0-9]+)\\s*</string>",
        "RevisionGroup": -1
      },
    ]

  },
  {
    "FileName": "Droid/Properties/AndroidManifest.xml",
    "Entries": [
      {
        "Pattern": "android:versionCode\\s*=\\s*\"([0-9]+)\"",
        "MajorGroup": -1,
        "MinorGroup": -1,
        "BuildGroup": 0,
        "RevisionGroup": -1
      },
      {
        "Pattern": "android:versionName\\s*=\\s*\"([0-9]+)\\.([0-9]+)\\.([0-9]+)\\s*\"",
        "RevisionGroup": -1
      }
    ]
  },
  {
    "FileName": "CommonAssemblyInfo.cs",
    "Entries": [
      {
        "Pattern": "AssemblyVersion\\(\"([0-9]+)\\.([0-9]+)\\.([0-9]+)\\.([0-9*]+)\"\\)"
      },
      {
        "Pattern": "AssemblyFileVersion\\(\"([0-9]+)\\.([0-9]+)\\.([0-9]+)\\.([0-9*]+)\"\\)"
      }
    ]
  },
  {
    "FileName": "SafeNotebooks.sln",
    "Entries": [
      {
        "Pattern": "version\\s*=\\s*([0-9]+)\\.([0-9]+)\\.([0-9]+)\\.([0-9*]+)"
      }
    ]
  },
  {
    "FileNames": [
      "Droid/Droid.csproj",
      "iOS/iOS.csproj",
      "macOS/macOS.csproj",
      "Shared/Shared.shproj",
      "Texts/Texts.csproj",
    ],
    "Entries": [
      {
        "Pattern": "<ReleaseVersion>\\s*([0-9]+)\\.([0-9]+)\\.([0-9]+)\\.([0-9]+)\\s*</ReleaseVersion>"
      }
    ]

  },
]
```