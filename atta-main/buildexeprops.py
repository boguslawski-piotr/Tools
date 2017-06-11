import platform
from atta import Atta

system = platform.system().lower()

installBaseDirName = 'archive'
installDirName = '%s/%s' % (installBaseDirName, Atta.version)
platformInstallDirName = installDirName

archiveFileName = 'Atta'

exeExt = ''

if system.startswith('win'):
  platformInstallDirName += '/win'
  archiveFileName += '-win'
  exeExt = '.exe'
elif system.startswith('linux'):
  platformInstallDirName += '/linux'
  archiveFileName += '-linux'
else:
  raise RuntimeError('Not known platform: %s' % platform.system())

archiveFileName += '-%s.zip' % Atta.version
