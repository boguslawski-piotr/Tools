using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using Newtonsoft.Json;

namespace Versions {
	public class Versions {
		readonly TextWriter _msgOut;
		readonly TextWriter _errOut;

		class File {
			public string FileName = "";
			public List<string> FileNames;
			public List<Entry> Entries;
		};

		class Entry {
			public string Pattern = "";
			public int MajorGroup = 0;
			public int MinorGroup = 1;
			public int BuildGroup = 2;
			public int RevisionGroup = 3;
		};

		enum Number {
			Major,
			Minor,
			Build,
			Revision,
		}

		enum Operation {
			Inc,
			Dec,
			Set,
			Add,
			Sub,
		};

		public Versions(TextWriter msgOut, TextWriter errOut) {
			_msgOut = msgOut;
			_errOut = errOut;
		}

		public void Process(string[] args) {
			Number currentNumber = Number.Revision;
			Operation currentOperation = Operation.Inc;
			string currentValue = null;
			bool nextShouldBeValue = false;

			foreach (var arg in args) {
				if (string.IsNullOrWhiteSpace(arg))
					continue;

				if (arg.StartsWith("--", StringComparison.Ordinal)) {
					if (!Enum.TryParse<Number>(arg.Substring(2), true, out Number number)) {
						if (!Enum.TryParse<Operation>(arg.Substring(2), true, out Operation operation)) {
							_errOut?.WriteLine($"Incorrect parameter: {arg}");
						} else {
							if (operation > Operation.Dec) nextShouldBeValue = true;
							currentOperation = operation;
						}
					} else {
						currentNumber = number;
					}
				} else {
					if (nextShouldBeValue) {
						currentValue = arg;
						nextShouldBeValue = false;
					} else {
						string currentValueDesc = (currentOperation == Operation.Set) ? "to " + currentValue : null;
						_msgOut?.WriteLine($"Loading: \"{Path.GetFullPath(arg)}\" to process: {currentNumber} {currentOperation} {currentValueDesc}");
						try {
							using (StreamReader s = System.IO.File.OpenText(arg)) {
								string json = s.ReadToEnd();
								string path = Path.GetDirectoryName(arg);
								foreach (File v in JsonConvert.DeserializeObject<List<File>>(json)) {
									try {
										Process(path, v, currentNumber, currentOperation, currentValue);
									} catch (FileNotFoundException ex) {
										_errOut?.WriteLine(ex.Message);
										continue;
									}
								}
							}
						} catch (Exception ex) {
							_errOut?.WriteLine(ex.Message);
							continue;
						}

						Console.WriteLine("");
					}
				}
			}
		}

		void Process(string path, File v, Number number, Operation operation, string value) {
			List<string> fileNames = v.FileNames;
			if (fileNames == null) {
				fileNames = new List<string>() {
					v.FileName,
				};
			}

			foreach (var vfn in fileNames) {
				string fileName = Path.GetFullPath(Path.Combine(path, vfn));
				_msgOut?.WriteLine($"Processing: \"{fileName}\"");

				string d = null;
				using (StreamReader reader = System.IO.File.OpenText(fileName))
					d = reader.ReadToEnd();

				foreach (var entry in v.Entries) {
					int groupToProcess = -1;
					if (number == Number.Major) groupToProcess = entry.MajorGroup;
					if (number == Number.Minor) groupToProcess = entry.MinorGroup;
					if (number == Number.Build) groupToProcess = entry.BuildGroup;
					if (number == Number.Revision) groupToProcess = entry.RevisionGroup;
					if (groupToProcess < 0) {
						_msgOut?.WriteLine($"Pattern: {entry.Pattern} has no assigned group for: {number}");
						continue;
					}

					Match m = Regex.Match(d, entry.Pattern);
					if (!m.Success) {
						_msgOut?.WriteLine($"No match for pattern: {entry.Pattern}");
						continue;
					}
					if (groupToProcess > m.Groups.Count - 2) {
						_msgOut?.WriteLine($"Entry with pattern: {entry.Pattern} has invalid group for: {number}");
						continue;
					}

					_msgOut?.WriteLine($"Found: {m.ToString()}");

					Group g = m.Groups[groupToProcess + 1]; // first group equals to whole match
					string lvalue = value;

					if (operation != Operation.Set) {
						if (int.TryParse(g.ToString(), out int n)) {
							switch (operation) {
								case Operation.Inc:
									n++;
									break;
								case Operation.Dec:
									n--;
									break;
								case Operation.Add:
									n = n + int.Parse(lvalue);
									break;
								case Operation.Sub:
									n = n - int.Parse(lvalue);
									break;
							}

							lvalue = n.ToString();
						} else {
							_errOut?.WriteLine($"Group {groupToProcess}: has incorrect number: {g.ToString()}");
							lvalue = null;
						}
					}

					if (lvalue != null) {
						_msgOut?.WriteLine($"For group: {groupToProcess} changing: {g.ToString()} to {lvalue}");

						string ds = d.Substring(0, g.Index);
						string de = d.Substring(g.Index + g.Length);
						d = ds + lvalue + de;

						using (StreamWriter writer = System.IO.File.CreateText(fileName))
							writer.Write(d);
					}
				}
			}
		}
	}
}
