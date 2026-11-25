"""Windows Credential Manager storage; no third-party dependencies."""

from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes


TARGET = "codex/bilibili-research/session"
CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2
ERROR_NOT_FOUND = 1168


class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


PCREDENTIAL = ctypes.POINTER(CREDENTIAL)
advapi32 = ctypes.WinDLL("Advapi32.dll", use_last_error=True) if os.name == "nt" else None
if advapi32:
    advapi32.CredWriteW.argtypes = [PCREDENTIAL, wintypes.DWORD]
    advapi32.CredWriteW.restype = wintypes.BOOL
    advapi32.CredReadW.argtypes = [wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(PCREDENTIAL)]
    advapi32.CredReadW.restype = wintypes.BOOL
    advapi32.CredDeleteW.argtypes = [wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    advapi32.CredDeleteW.restype = wintypes.BOOL
    advapi32.CredFree.argtypes = [ctypes.c_void_p]


def windows_error(action: str) -> RuntimeError:
    code = ctypes.get_last_error()
    return RuntimeError(f"{action}失败（Windows 错误 {code}）")


def save_session(payload: dict) -> None:
    if not advapi32:
        raise RuntimeError("当前凭据实现仅支持 Windows")
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    buffer = ctypes.create_string_buffer(raw)
    credential = CREDENTIAL()
    credential.Type = CRED_TYPE_GENERIC
    credential.TargetName = TARGET
    credential.Comment = "Bilibili Research session; managed by Codex"
    credential.CredentialBlobSize = len(raw)
    credential.CredentialBlob = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte))
    credential.Persist = CRED_PERSIST_LOCAL_MACHINE
    credential.UserName = "bilibili"
    if not advapi32.CredWriteW(ctypes.byref(credential), 0):
        raise windows_error("保存 Windows 凭据")


def load_session() -> dict | None:
    if not advapi32:
        raise RuntimeError("当前凭据实现仅支持 Windows")
    pointer = PCREDENTIAL()
    if not advapi32.CredReadW(TARGET, CRED_TYPE_GENERIC, 0, ctypes.byref(pointer)):
        if ctypes.get_last_error() == ERROR_NOT_FOUND:
            return None
        raise windows_error("读取 Windows 凭据")
    try:
        credential = pointer.contents
        raw = ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("cookies"), dict):
            raise RuntimeError("Windows 凭据格式无效；请重新扫码登录")
        return payload
    finally:
        advapi32.CredFree(pointer)


def delete_session() -> bool:
    if not advapi32:
        raise RuntimeError("当前凭据实现仅支持 Windows")
    if advapi32.CredDeleteW(TARGET, CRED_TYPE_GENERIC, 0):
        return True
    if ctypes.get_last_error() == ERROR_NOT_FOUND:
        return False
    raise windows_error("删除 Windows 凭据")

