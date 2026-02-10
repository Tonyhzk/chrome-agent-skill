"""
批量获取网页跳转链接的真实目标URL模板

使用方式:
    python3 batch_resolve_urls.py --config config.json
    python3 batch_resolve_urls.py --urls urls.txt --output result.md

配置文件格式 (config.json):
    {
        "links": [
            {"name": "示例网站", "url": "https://example.com/jump/site1"},
            {"name": "另一个网站", "url": "https://example.com/jump/site2"}
        ],
        "output": "output.md",
        "extract_patterns": [
            "goToLink\\(\\d+,\\s*'(https?://[^']+)'",
            "window\\.location\\s*=\\s*[\"'](https?://[^\"']+)"
        ],
        "delay": 0.3,
        "title": "网站链接汇总",
        "description": "来源说明"
    }

URL文件格式 (urls.txt，每行一个，名称和URL用制表符或 | 分隔):
    Web of Science | https://example.com/jump/wos
    Nature | https://example.com/jump/nature
"""
import argparse
import json
import re
import sys
import time

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# 默认提取模式：覆盖常见的前端跳转方式
DEFAULT_PATTERNS = [
    r"goToLink\(\d+,\s*'(https?://[^']+)'",
    r'goToLink\(\d+,\s*"(https?://[^"]+)"',
    r"window\.location(?:\.href)?\s*=\s*[\"'](https?://[^\"']+)",
    r'<meta[^>]*url=(https?://[^"\'>\s]+)',
    r'data-url=["\']?(https?://[^"\'>\s]+)',
]


def resolve_url(name, jump_url, patterns, base_domain=None):
    """请求跳转页面，通过正则提取真实URL"""
    try:
        resp = requests.get(jump_url, allow_redirects=True, timeout=15, headers=HEADERS)

        # 如果 HTTP 重定向到了外部域名，直接返回
        if base_domain and base_domain not in resp.url:
            return resp.url

        # 从页面内容中用正则提取
        for pattern in patterns:
            match = re.search(pattern, resp.text, re.IGNORECASE)
            if match:
                url = match.group(1)
                if base_domain and base_domain not in url:
                    return url
                # 即使包含 base_domain 也返回（可能就是目标）
                return url

        return "未找到真实链接"
    except Exception as e:
        return f"请求失败: {e}"


def load_from_config(config_path):
    """从 JSON 配置文件加载"""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    links = [(item["name"], item["url"]) for item in config["links"]]
    patterns = config.get("extract_patterns", DEFAULT_PATTERNS)
    # 如果配置中的 pattern 是字符串，直接用；不需要额外转义
    return {
        "links": links,
        "patterns": patterns,
        "output": config.get("output", "output.md"),
        "delay": config.get("delay", 0.3),
        "title": config.get("title", "链接汇总"),
        "description": config.get("description", ""),
    }


def load_from_file(urls_path):
    """从文本文件加载 URL 列表"""
    links = []
    with open(urls_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                parts = line.split("|", 1)
            elif "\t" in line:
                parts = line.split("\t", 1)
            else:
                parts = [line, line]
            name = parts[0].strip()
            url = parts[1].strip() if len(parts) > 1 else name
            links.append((name, url))
    return links


def write_markdown(results, output_path, title, description):
    """将结果写入 Markdown 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        if description:
            f.write(f"> {description}\n\n")
        f.write("| 序号 | 名称 | 链接 |\n")
        f.write("|------|------|------|\n")
        for i, (name, real_url) in enumerate(results, 1):
            f.write(f"| {i} | {name} | {real_url} |\n")


def main():
    parser = argparse.ArgumentParser(description="批量解析跳转链接的真实目标URL")
    parser.add_argument("--config", help="JSON 配置文件路径")
    parser.add_argument("--urls", help="URL 列表文件路径（每行: 名称 | URL）")
    parser.add_argument("--output", default="output.md", help="输出文件路径")
    parser.add_argument("--delay", type=float, default=0.3, help="请求间隔秒数")
    parser.add_argument("--title", default="链接汇总", help="文档标题")
    parser.add_argument("--description", default="", help="文档描述")
    args = parser.parse_args()

    if args.config:
        config = load_from_config(args.config)
        links = config["links"]
        patterns = config["patterns"]
        output = args.output if args.output != "output.md" else config["output"]
        delay = args.delay if args.delay != 0.3 else config["delay"]
        title = args.title if args.title != "链接汇总" else config["title"]
        description = args.description or config["description"]
    elif args.urls:
        links = load_from_file(args.urls)
        patterns = DEFAULT_PATTERNS
        output = args.output
        delay = args.delay
        title = args.title
        description = args.description
    else:
        print("请指定 --config 或 --urls 参数")
        sys.exit(1)

    # 自动推断 base_domain（跳转页面的域名）
    from urllib.parse import urlparse
    domains = set()
    for _, url in links:
        parsed = urlparse(url)
        if parsed.netloc:
            domains.add(parsed.netloc)
    base_domain = domains.pop() if len(domains) == 1 else None

    results = []
    total = len(links)
    for i, (name, url) in enumerate(links, 1):
        print(f"[{i}/{total}] {name} ...", end=" ", flush=True)
        real_url = resolve_url(name, url, patterns, base_domain)
        print(real_url)
        results.append((name, real_url))
        if i < total:
            time.sleep(delay)

    write_markdown(results, output, title, description)
    print(f"\n完成！共 {len(results)} 个，已写入: {output}")


if __name__ == "__main__":
    main()
