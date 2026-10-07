# searching job

[English (Australian)](README.md)

适用于任意行业的求职外联短名单 skill。配好关键词与筛选条件后，助手在 SEEK / Indeed / LinkedIn Jobs 搜索，补齐公司地址、人数与一位联系人，并用自带脚本输出固定格式 digest。除非你明确要求，否则不会代发外联。

MIT — 见 [LICENSE](LICENSE)。

## 安装

```bash
git clone https://github.com/LinxiaoJiang/searching-job.git
cd searching-job
cp config.example.json config.json
```

也可从 [Releases](https://github.com/LinxiaoJiang/searching-job/releases) 下载 zip。

编辑 `config.json` 后检查：

```bash
python3 scripts/load_config.py
```

| 字段 | 说明 |
|---|---|
| `search_keywords` | **必填。** 岗位搜索词。 |
| `location` | 如 `Melbourne VIC`。 |
| `min_company_size` / `max_company_size` | 公司人数上下限；`0` = 不检查。 |
| `target_company_count` | 每次目标公司数（默认 `5`）。 |
| `backfill_company_keywords` | 有广告不足目标时搜相关公司的词；空则从 `search_keywords` 推导。 |
| `other_requirements` | 调研时由助手执行的自由文本规则。 |

## 凑满目标

目标 `target_company_count` 家：

1. 优先有匹配广告的公司。
2. 有广告 ≥ 目标 → 停止，不再补无空缺。
3. 有广告 < 目标 → 保留广告公司，再补相关公司（可无空缺）。
4. 有广告 = 0 → 只列相关公司，最多目标数。

## 流水线

```bash
python3 scripts/filter_candidates.py -i candidates.json --rejected rejected.json > kept.json
python3 scripts/format_digest.py -i kept.json -o digest.md
python3 scripts/validate_digest.py digest.md
```

仅在出现 `validate_digest OK` 后贴出 digest，禁止手写格式。

试跑示例（先在临时 config 里填好 `search_keywords`）：

```bash
python3 scripts/filter_candidates.py -i examples/sample_candidates.json --config /path/to/config.json > /tmp/kept.json
python3 scripts/format_digest.py -i /tmp/kept.json -o /tmp/digest.md
python3 scripts/validate_digest.py /tmp/digest.md
```

### 候选字段

`company`、`job_title`、`ad_url`（无空缺可用 `none` / `has_ad: false`）、`website`、`street_address`、`suburb`、`headcount`、`lead_name`、`lead_title`，可选 `lead_linkedin` / `lead_email`。

## 摘要格式

不编号。每家公司 3 个字段，字段间空一行；公司之间 `---` 再 `---`。

```
**Company** — Full job title — [ad](url)

Street, Suburb — headcount — [website](url)

Name — title — [LinkedIn](url) — email|none
```

无空缺：`**Company** — Company outreach (no open ad) — none`。

## 目录

```
SKILL.md · config.example.json · scripts/ · examples/ · README*.md · LICENSE
```

Python 3.8+，无第三方依赖。平台：SEEK、Indeed、LinkedIn Jobs。
