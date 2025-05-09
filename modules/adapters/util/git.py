from __future__ import annotations
from typing import Callable

from ...import core

from .import vscode
from .import request

import string

class GitInstaller(vscode.AdapterInstaller):
	def __init__(self, type: str, repo: str, is_valid_asset: Callable[[str], bool] = lambda asset: asset.endswith('.vsix')):
		self.type = type
		self.repo = repo
		self.is_valid_asset = is_valid_asset

	async def install(self, version: str, log: core.Logger):
		releases = await request.json(f'https://api.github.com/repos/{self.repo}/releases')
		for release in releases:
			if version != version_from_release(release):
				continue

			for asset in release.get('assets', []):
				if self.is_valid_asset(asset['name']):
					return await self.install_from_asset(asset['browser_download_url'], log)

		raise core.Error(f'Unable to find a suitable release in {self.repo}')

	async def installable_versions(self, log: core.Logger) -> list[str]:
		try:
			releases = await request.json(f'https://api.github.com/repos/{self.repo}/releases')
			versions: list[str] = []

			for release in releases:
				version = version_from_release(release)
				if not version:
					continue

				for asset in release.get('assets', []):
					if self.is_valid_asset(asset['name']):
						versions.append(version)
						break

			return versions

		except Exception as e:
			log.error(f'{self.type}: {e}')
			raise e


class GitSourceInstaller(vscode.AdapterInstaller):
	def __init__(self, type: str, repo: str):
		self.type = type
		self.repo = repo

	async def install(self, version: str|None, log: core.Logger):
		releases = await request.json(f'https://api.github.com/repos/{self.repo}/releases')
		for release in releases:
			if version == version_from_release(release):
				return await self.install_from_asset(release['zipball_url'], log)

		raise core.Error(f'Unable to find a suitable release in {self.repo}')

	async def installable_versions(self, log: core.Logger) -> list[str]:
		try:
			releases = await request.json(f'https://api.github.com/repos/{self.repo}/releases')
			versions: list[str] = []

			for release in releases:
				if version := version_from_release(release):
					versions.append(version)

			return versions

		except Exception as e:
			log.error(f'{self.type}: {e}')
			raise e

def version_from_release(release: core.JSON):
	# remove anything that isn't a number from the start of a tag
	# lots of tags include a prefix like v
	version: str = release.tag_name
	version = version.lstrip(string.punctuation + string.ascii_letters)

	if release.draft:
		return f'{version} (draft)'

	if release.prerelease:
		return f'{version} (prerelease)'

	return version
