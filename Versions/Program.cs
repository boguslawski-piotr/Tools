using System;

namespace Versions
{
	class MainClass
	{
		public static void Main(string[] args)
		{
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
			Console.WriteLine("Help..."); // TODO: write nice help...
		}
	}
}
