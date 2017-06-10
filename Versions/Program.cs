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
					Console.WriteLine($"Loading {arg} for process {whichNumber}");
					try
					{
						using (StreamReader s = File.OpenText(arg))
						{
							string json = s.ReadToEnd();
							foreach (Version _v in JsonConvert.DeserializeObject<List<Version>>(json))
								Process(_v, whichNumber);
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
			Console.WriteLine($"  Processing {whichNumber} in {v.FileName}");

			int groupToProcess = -1;
			if (whichNumber == Number.Major) groupToProcess = v.MajorGroup;
			if (whichNumber == Number.Minor) groupToProcess = v.MinorGroup;
			if (whichNumber == Number.Build) groupToProcess = v.BuildGroup;
			if (whichNumber == Number.Revision) groupToProcess = v.RevisionGroup;
			if (groupToProcess == -1)
			{
				Console.WriteLine($"    {whichNumber} has no assigned group, skiping");
				return;
			}

			string d = null;
			using (StreamReader s = File.OpenText(v.FileName))
				d = s.ReadToEnd();

			foreach (var i in v.Items)
			{
				Match m = Regex.Match(d, i);
				if (m.Success)
				{
					Console.WriteLine($"    Found: {m.ToString()}");
					int group = 0;
					foreach (var gs in m.Groups)
					{
						if (group > 0) // first group equals to whole match
						{
							if (group - 1 == groupToProcess && gs is Group g)
							{
								if (int.TryParse(g.ToString(), out int n))
								{
									Console.WriteLine($"      for group {group - 1} changing {n} to {n + 1}");

									n++;
									string ds = d.Substring(0, g.Index);
									string de = d.Substring(g.Index + g.Length);
									d = ds + n.ToString() + de;

									using (StreamWriter writer = File.CreateText(v.FileName))
										writer.Write(d);
								}
								else
									Console.WriteLine($"      group {group} has incorrect number: {g.ToString()}");
							}
						}

						group++;
					}
				}
			}
		}

		static void DisplayHelp()
		{
			Console.WriteLine("Help...");
		}
	}
}
