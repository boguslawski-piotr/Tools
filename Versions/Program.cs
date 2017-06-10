using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using Newtonsoft.Json;

namespace Versions
{
	class MainClass
	{
		class Version
		{
			public string FileName;
			public List<string> Items;

			public int MajorGroup = 0;
			public int MinorGroup = 1;
			public int BuildGroup = 2;
			public int RevisionGroup = 3;
		};

		enum Number
		{
			Major,
			Minor,
			Build,
			Revision,
		}

		public static void Main(string[] args)
		{
			Number whichNumber = Number.Revision;
			foreach (var arg in args)
			{
				if (arg.StartsWith("--", StringComparison.Ordinal))
				{
					if (arg == "--help")
						DisplayHelp();
					else
					{
						if (!Enum.TryParse<Number>(arg.Substring(2), true, out whichNumber))
							Console.WriteLine($"Incorrect parameter: {arg}");
					}
				}
				else
				{
					Console.WriteLine($"Loading: {arg} to process: {whichNumber}");
					try
					{
						using (StreamReader s = File.OpenText(arg))
						{
							string json = s.ReadToEnd();
							foreach (Version v in JsonConvert.DeserializeObject<List<Version>>(json))
								Process(v, whichNumber);
						}
					}
					catch (Exception ex)
					{
						Console.Error.WriteLine("  " + ex.Message);
						continue;
					}

					Console.WriteLine("");
				}
			}
		}

		static void Process(Version v, Number whichNumber)
		{
			Console.WriteLine($"  Processing: {whichNumber} in: {v.FileName}");

			int groupToProcess = -1;
			if (whichNumber == Number.Major) groupToProcess = v.MajorGroup;
			if (whichNumber == Number.Minor) groupToProcess = v.MinorGroup;
			if (whichNumber == Number.Build) groupToProcess = v.BuildGroup;
			if (whichNumber == Number.Revision) groupToProcess = v.RevisionGroup;
			if (groupToProcess == -1)
			{
				Console.WriteLine($"    {whichNumber} has no assigned group");
				return;
			}

			string d = null;
			using (StreamReader reader = File.OpenText(v.FileName))
				d = reader.ReadToEnd();

			foreach (var pattern in v.Items)
			{
				Match m = Regex.Match(d, pattern);
				if (!m.Success)
				{
					Console.WriteLine($"    No match for: {pattern}");
					continue;
				}

				Console.WriteLine($"    Found: {m.ToString()}");

				int currentGroup = 0;
				foreach (Group g in m.Groups)
				{
					// first group equals to whole match
					if (currentGroup > 0 && currentGroup - 1 == groupToProcess)
					{
						if (int.TryParse(g.ToString(), out int n))
						{
							Console.WriteLine($"      For group: {currentGroup - 1} changing: {n} to {n + 1}");

							n++;
							string ds = d.Substring(0, g.Index);
							string de = d.Substring(g.Index + g.Length);
							d = ds + n.ToString() + de;

							using (StreamWriter writer = File.CreateText(v.FileName))
								writer.Write(d);
						}
						else
							Console.WriteLine($"      Group {currentGroup}: has incorrect number: {g.ToString()}");
					}

					currentGroup++;
				}
			}
		}

		static void DisplayHelp()
		{
			Console.WriteLine("Help...");
		}
	}
}
