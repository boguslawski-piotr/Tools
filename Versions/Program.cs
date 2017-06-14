using System;

namespace Versions
{
	class MainClass
	{
		public static void Main(string[] args)
		{
			if(args.Length <= 0)
			{
				DisplayHelp();
				return;
			}

			foreach (var arg in args)
			{
				if (arg == "--help" || arg == "--?")
				{
					DisplayHelp();
					return;
				}
			}

			Versions v = new Versions(Console.Out, Console.Error);
			v.Process(args);
		}

		static void DisplayHelp()
		{
			Console.WriteLine("Usage: Versions [NUMBER] [OPERATION] FILE ...\n" +
							  "where:\n" +
							  "  NUMBER can be one of:\n" +
							  "    --major, --minor, --build, --revision (default)\n" +
							  "  OPERATION can be one of:\n" +
							  "    --inc (default), --dec\n" +
							  "    --set value, --add value, --sub value\n" +
							  "  and FILE is a simple json file with detailed\n" +
							  "  definition of what and how will be processed." +
							  "");
			
			Console.WriteLine("\nPress Enter/Return for examples...");
			Console.ReadLine();

			Console.WriteLine("Versions --minor FILE\n" +
							  "  increments (adds 1) minor version numbers whose definitions are written in FILE\n" +
			                  "\nVersions --build --add 2 FILE1 FILE2\n" +
			                  "  adds 2 to build numbers whose definitions are written in FILE1 and FILE2\n" +
			                  "\nVersions --revision --inc FILE1 --build --set 23 FILE2\n" +
			                  "  increments revision numbers (taking definitions from FILE1)\n" +
			                  "  and sets build numbers to 23 (taking definitions from FILE2)"
			                 );

			Console.WriteLine("\nPress Enter/Return for example json file...");
			Console.ReadLine();
			Console.WriteLine("Example of FILE with definitions, showing different possibilities:\n" +
			                  "[\n  {\n    \"FileNames\": [\n      \"iOS/Info.plist\",\n      \"macOS/Info.plist\"\n    ],\n    \"Entries\": [\n      {\n        \"Pattern\": \"<key>CFBundleShortVersionString</key>\\\\s*<string>\\\\s*([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\s*</string>\",\n        \"RevisionGroup\": -1\n      },\n      {\n        \"Pattern\": \"<key>CFBundleVersion</key>\\\\s*<string>\\\\s*([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\s*</string>\",\n        \"RevisionGroup\": -1\n      },\n    ]\n\n  },\n  {\n    \"FileName\": \"Droid/Properties/AndroidManifest.xml\",\n    \"Entries\": [\n      {\n        \"Pattern\": \"android:versionCode\\\\s*=\\\\s*\\\"([0-9]+)\\\"\",\n        \"MajorGroup\": -1,\n        \"MinorGroup\": -1,\n        \"BuildGroup\": 0,\n        \"RevisionGroup\": -1\n      },\n      {\n        \"Pattern\": \"android:versionName\\\\s*=\\\\s*\\\"([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\s*\\\"\",\n        \"RevisionGroup\": -1\n      }\n    ]\n  },\n  {\n    \"FileName\": \"CommonAssemblyInfo.cs\",\n    \"Entries\": [\n      {\n        \"Pattern\": \"AssemblyVersion\\\\(\\\"([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\.([0-9*]+)\\\"\\\\)\"\n      },\n      {\n        \"Pattern\": \"AssemblyFileVersion\\\\(\\\"([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\.([0-9*]+)\\\"\\\\)\"\n      }\n    ]\n  },\n  {\n    \"FileName\": \"SafeNotebooks.sln\",\n    \"Entries\": [\n      {\n        \"Pattern\": \"version\\\\s*=\\\\s*([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\.([0-9*]+)\"\n      }\n    ]\n  },\n  {\n    \"FileNames\": [\n      \"Droid/Droid.csproj\",\n      \"iOS/iOS.csproj\",\n      \"macOS/macOS.csproj\",\n      \"Shared/Shared.shproj\",\n      \"Texts/Texts.csproj\",\n    ],\n    \"Entries\": [\n      {\n        \"Pattern\": \"<ReleaseVersion>\\\\s*([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\.([0-9]+)\\\\s*</ReleaseVersion>\"\n      }\n    ]\n\n  },\n]"
							 );
		}
	}
}
