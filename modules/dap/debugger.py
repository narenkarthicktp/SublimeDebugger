from __future__ import annotations
from typing import TYPE_CHECKING, Any, Protocol


from ..import core

if TYPE_CHECKING:
	from .adapter import AdapterConfiguration
	from .configuration import ConfigurationExpanded

	from ..breakpoints import Breakpoints
	from . import Session
	from . import OutputEvent
	from .variable import SourceLocation

class Debugger(Protocol):
	on_session_added: core.Event[Session]
	on_session_removed: core.Event[Session]
	on_session_active: core.Event[Session]

	on_session_modules_updated: core.Event[Session]
	on_session_sources_updated: core.Event[Session]
	on_session_variables_updated: core.Event[Session]
	on_session_threads_updated: core.Event[Session]
	on_session_state_updated: core.Event[Session, Session.State]
	on_session_output: core.Event[Session, OutputEvent]

	sessions: list[Session]
	session: Session|None
	console: Console

	async def launch(self, breakpoints: Breakpoints, adapter: AdapterConfiguration, configuration: ConfigurationExpanded, restart: Any|None = None, no_debug: bool = False, parent: Session|None = None) -> Session: ...


class Console(core.Logger, Protocol):
	def error(self, text: str, source: SourceLocation|None = None):
		self.log('error', text, source)

	def info(self, text: str, source: SourceLocation|None = None):
		self.log('comment', text, source)

	def log(self, type: str, value: Any, source: SourceLocation|None = None): ...
