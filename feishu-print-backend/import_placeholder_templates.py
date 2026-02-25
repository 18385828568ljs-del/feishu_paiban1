import argparse
import json
import sys
import urllib.error
import urllib.request


def _post_json(url: str, payload: dict, timeout: int) -> tuple[int, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body


def _get_json(url: str, timeout: int) -> tuple[int, dict | None, str]:
    req = urllib.request.Request(
        url=url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body), body
            except json.JSONDecodeError:
                return resp.status, None, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body), body
        except json.JSONDecodeError:
            return e.code, None, body


def _detect_templates_endpoint(base_url: str, timeout: int) -> str | None:
    base_url = base_url.rstrip("/")

    openapi_url = base_url + "/openapi.json"
    status, openapi, raw = _get_json(openapi_url, timeout=timeout)
    if status != 200 or not isinstance(openapi, dict):
        return None

    paths = openapi.get("paths")
    if not isinstance(paths, dict):
        return None

    candidates = [
        "/api/templates/",
        "/api/templates",
        "/templates/",
        "/templates",
    ]

    for p in candidates:
        methods = paths.get(p)
        if not isinstance(methods, dict):
            continue
        if "post" in methods:
            return base_url + p

    # 兜底：在所有 path 里找包含 templates 且支持 post 的
    for p, methods in paths.items():
        if "templates" not in str(p).lower():
            continue
        if not isinstance(methods, dict):
            continue
        if "post" in methods:
            if str(p).startswith("/"):
                return base_url + str(p)
            return base_url + "/" + str(p)

    return None


def _traditional_html(i: int) -> str:
    return f"""
<p style=\"text-align:center;\"><span style=\"font-size:22pt;font-family:方正小标宋简体;\">传统-占位符模板{i:02d}</span></p>
<p style=\"text-align:right;\"><span style=\"font-family:仿宋;\">编号：{{$编号}}　日期：{{$日期}}</span></p>
<table style=\"border-collapse:collapse;width:100%;\" border=\"1\">
  <colgroup>
    <col style=\"width:20%;\" />
    <col style=\"width:30%;\" />
    <col style=\"width:20%;\" />
    <col style=\"width:30%;\" />
  </colgroup>
  <tbody>
    <tr>
      <td><span style=\"font-family:仿宋;\">姓名</span></td>
      <td><span style=\"font-family:仿宋;\" class=\"template-field field-block\" contenteditable=\"false\" data-fieldname=\"姓名\">{{$姓名}}</span></td>
      <td><span style=\"font-family:仿宋;\">部门</span></td>
      <td><span style=\"font-family:仿宋;\" class=\"template-field field-block\" contenteditable=\"false\" data-fieldname=\"部门\">{{$部门}}</span></td>
    </tr>
    <tr>
      <td><span style=\"font-family:仿宋;\">事项</span></td>
      <td colspan=\"3\"><span style=\"font-family:仿宋;\" class=\"template-field field-block\" contenteditable=\"false\" data-fieldname=\"事项\">{{$事项}}</span></td>
    </tr>
    <tr>
      <td><span style=\"font-family:仿宋;\">备注</span></td>
      <td colspan=\"3\"><span style=\"font-family:仿宋;\">（在编辑器中补充内容）</span></td>
    </tr>
  </tbody>
</table>
<p style=\"font-family:仿宋;\">审批人：{{$审批人}}　签名：{{$签名}}</p>
""".strip()


def _modern_html(i: int) -> str:
    return f"""
<div style=\"font-family:Arial, PingFang SC, Microsoft YaHei, sans-serif;\">
  <div style=\"display:flex;justify-content:space-between;align-items:flex-end;\">
    <div style=\"font-size:20px;font-weight:700;\">现代-占位符模板{i:02d}</div>
    <div style=\"font-size:12px;color:#666;\">{{$日期}}　{{$编号}}</div>
  </div>
  <div style=\"height:1px;background:#e5e7eb;margin:12px 0 16px;\"></div>

  <div style=\"display:grid;grid-template-columns:1fr 1fr;gap:12px;\">
    <div style=\"border:1px solid #e5e7eb;border-radius:10px;padding:12px;\">
      <div style=\"font-size:12px;color:#6b7280;margin-bottom:6px;\">姓名</div>
      <div style=\"font-size:14px;font-weight:600;\">{{$姓名}}</div>
    </div>
    <div style=\"border:1px solid #e5e7eb;border-radius:10px;padding:12px;\">
      <div style=\"font-size:12px;color:#6b7280;margin-bottom:6px;\">部门</div>
      <div style=\"font-size:14px;font-weight:600;\">{{$部门}}</div>
    </div>
  </div>

  <div style=\"margin-top:12px;border:1px solid #e5e7eb;border-radius:10px;padding:12px;\">
    <div style=\"font-size:12px;color:#6b7280;margin-bottom:6px;\">内容</div>
    <div style=\"font-size:14px;line-height:1.7;color:#111827;\">{{$内容}}</div>
  </div>

  <div style=\"margin-top:14px;display:flex;justify-content:space-between;color:#6b7280;font-size:12px;\">
    <div>创建人：{{$创建人}}</div>
    <div>签名：{{$签名}}</div>
  </div>
</div>
""".strip()


def _build_templates(traditional_count: int, modern_count: int, name_suffix: str) -> list[dict]:
    name_suffix = name_suffix or ""

    templates: list[dict] = []
    for i in range(1, traditional_count + 1):
        templates.append(
            {
                "name": f"传统-占位符模板{i:02d}{name_suffix}",
                "content": _traditional_html(i),
            }
        )
    for i in range(1, modern_count + 1):
        templates.append(
            {
                "name": f"现代-占位符模板{i:02d}{name_suffix}",
                "content": _modern_html(i),
            }
        )

    return templates


def main() -> int:
    parser = argparse.ArgumentParser(description="批量导入占位符模板（10传统+10现代）")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="后端地址，例如 http://localhost:8000",
    )
    parser.add_argument(
        "--endpoint",
        default="",
        help="手动指定创建模板接口完整地址（优先级高于自动探测），例如 http://localhost:8000/api/templates/",
    )
    parser.add_argument("--traditional", type=int, default=10, help="传统模板数量")
    parser.add_argument("--modern", type=int, default=10, help="现代模板数量")
    parser.add_argument(
        "--name-suffix",
        default="",
        help="模板名称后缀（可用于区分多次导入，例如 -v1 或 -20260118）",
    )
    parser.add_argument("--timeout", type=int, default=15, help="请求超时秒数")
    parser.add_argument(
        "--fail-on-exists",
        action="store_true",
        help="遇到模板名称已存在（HTTP 400）时直接失败；默认是跳过",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    # 预检：health + openapi（用于定位是否连到了正确的后端）
    health_status, _, _ = _get_json(base_url + "/health", timeout=args.timeout)
    openapi_status, openapi_json, _ = _get_json(base_url + "/openapi.json", timeout=args.timeout)
    print(f"预检: GET /health -> {health_status}; GET /openapi.json -> {openapi_status}")

    endpoint = args.endpoint.strip()
    if not endpoint:
        detected = _detect_templates_endpoint(base_url, timeout=args.timeout)
        if detected:
            endpoint = detected
        else:
            if isinstance(openapi_json, dict) and isinstance(openapi_json.get("paths"), dict):
                available = list(openapi_json["paths"].keys())
                available_preview = "\n".join([f"- {p}" for p in available[:60]])
                print("\n未在 OpenAPI 中发现可用的 templates POST 接口。")
                print("这通常表示：你连到的不是当前项目后端，或后端未启动/未加载 templates 路由。")
                print("\n当前服务暴露的部分路径如下：")
                print(available_preview)
            else:
                print("\n无法读取 OpenAPI 定义（/openapi.json 不可用或非 JSON）。")
                print("请确认你启动的是本项目后端：uvicorn app.main:app --port 8000")

            return 2

    if not endpoint.endswith("/"):
        endpoint = endpoint + "/"

    print(f"使用接口: {endpoint}")
    templates = _build_templates(args.traditional, args.modern, args.name_suffix)

    created = 0
    skipped = 0
    failed = 0

    for idx, t in enumerate(templates, start=1):
        status, body = _post_json(endpoint, t, timeout=args.timeout)

        if status in (200, 201):
            created += 1
            print(f"[{idx}/{len(templates)}] 创建成功: {t['name']}")
            continue

        # FastAPI 校验/业务错误：模板名已存在会返回 400
        if status == 400:
            if args.fail_on_exists:
                print(f"[{idx}/{len(templates)}] 已存在且终止: {t['name']}\n{body}")
                return 2
            skipped += 1
            print(f"[{idx}/{len(templates)}] 已存在，跳过: {t['name']}")
            continue

        failed += 1
        print(f"[{idx}/{len(templates)}] 创建失败({status}): {t['name']}\n{body}")

    print("\n==== 导入结果 ====")
    print(f"目标数量: {len(templates)}")
    print(f"创建成功: {created}")
    print(f"已存在跳过: {skipped}")
    print(f"失败: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
