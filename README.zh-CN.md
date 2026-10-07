# searching job

[English (Australian)](README.md)

**searching job** 是一个适用于任何行业的求职外联（outreach）短名单 skill。你告诉它要找什么岗位、在哪里找、还有哪些其他要求；AI 助手会在 SEEK、Indeed 和 LinkedIn Jobs 上（不登录）搜索招聘广告，查找每家公司的办公地址、公司人数以及一位合适的联系人，最后生成格式固定、整洁的短名单摘要（digest）。

每次运行目标是推送可配置数量的公司（默认 **5 家**）：优先有招聘广告的公司；数量不足时再用相关公司补齐（即使暂无空缺）。摘要始终由仓库自带的 Python 脚本生成并校验，因此格式不会走样。本 skill 绝不会替你发送邮件、消息或求职申请。

## 许可证

采用 [MIT 许可证](LICENSE) 发布。

## 前置条件

- Python 3.8 或更高版本（无需安装第三方包）
- 能读取 `SKILL.md` 并能浏览网页的 AI 助手（用于调研步骤）
- Git（可选——也可以直接下载 Release 压缩包）

## 仓库内容

```
searching-job/
├── SKILL.md                    # 给 AI 助手的操作说明
├── config.example.json         # 配置模板——复制为 config.json
├── scripts/
│   ├── load_config.py          # 读取并校验 config.json
│   ├── filter_candidates.py    # 检查必填字段和公司人数区间
│   ├── format_digest.py        # 生成摘要
│   └── validate_digest.py      # 校验摘要格式
├── examples/
│   └── sample_candidates.json  # 用于试运行的虚构数据
├── README.md / README.zh-CN.md
└── LICENSE
```

## 初始化（逐步说明）

### 1. 获取文件

克隆仓库：

```bash
git clone https://github.com/LinxiaoJiang/searching-job.git
cd searching-job
```

或者在 **Releases** 页面下载 `searching-job-vX.Y.Z.zip`，解压后在终端中打开该文件夹。

如果你的 AI 助手从某个固定目录加载 skill，请把整个 `searching-job` 文件夹复制（或软链接）到那里。

### 2. 创建配置文件

```bash
cp config.example.json config.json
```

Windows（PowerShell）：`Copy-Item config.example.json config.json`

`config.json` 已写入 `.gitignore`，你的个人设置不会被提交到仓库。

### 3. 填写 `config.json`

```json
{
  "search_keywords": ["graduate data analyst", "junior business analyst"],
  "location": "Melbourne VIC",
  "min_company_size": 100,
  "max_company_size": 5000,
  "target_company_count": 5,
  "backfill_company_keywords": ["data analytics consultancy", "business intelligence"],
  "other_requirements": "Office-based or hybrid roles only. Skip ads that require security clearance."
}
```

| 字段 | 是否必填 | 填写内容 |
|---|---|---|
| `search_keywords` | **必填** | 一个或多个岗位关键词，就像你在 SEEK 搜索框里输入的那样。列表为空时脚本会拒绝运行。 |
| `location` | 建议填写 | 搜索的城市或地区，例如 `Melbourne VIC`、`Sydney NSW`、`Brisbane`。 |
| `min_company_size` | 建议填写 | 公司最低人数（与 LinkedIn 人数区间的下限比较，例如 `201-500` 按 201 计算）。填 `0` 表示不检查。 |
| `max_company_size` | 建议填写 | 公司最高人数（与 LinkedIn 人数区间的上限比较）。填 `0` 表示不检查。 |
| `target_company_count` | 建议填写 | 每次运行目标公司数量（默认 `5`）。 |
| `backfill_company_keywords` | 可选 | 当当天有广告的公司不足目标数量时，用来搜索相关公司的关键词。为空时，助手会从 `search_keywords` 推导。 |
| `other_requirements` | 可选 | 其他任何要求，用自然语言写即可。AI 助手在阅读每条广告或公司资料时会据此筛选。 |

检查配置是否正确：

```bash
python3 scripts/load_config.py
```

配置正确时会打印校验后的设置；否则会报错（退出码 2）并说明需要修改的地方。

### 4. 凑满目标数量的规则

每次运行目标是 `target_company_count` 家公司：

1. 优先保留有匹配招聘广告的公司。
2. 有广告的已达到目标：只保留有广告的，不再补无空缺公司。
3. 有广告的不足目标：保留这些，再用 `backfill_company_keywords`（或推导词）搜索相关公司补齐（可无空缺）。
4. 当天没有匹配广告：搜索最多目标数量的相关公司（可无空缺）。

### 5. 运行流程

让 AI 助手按照 `SKILL.md` 执行（例如对它说：“Run the searching job skill”）。它会调研招聘广告（必要时补齐公司），并把结果保存为 JSON 数组，例如 `candidates.json`。然后运行：

```bash
# 1) 保留必填字段齐全且满足人数区间的候选
python3 scripts/filter_candidates.py -i candidates.json --rejected rejected.json > kept.json

# 2) 生成摘要
python3 scripts/format_digest.py -i kept.json -o digest.md

# 3) 校验摘要——只有输出 "validate_digest OK" 才可以使用
python3 scripts/validate_digest.py digest.md
```

`load_config.py` 和 `filter_candidates.py` 支持 `--config 路径/config.json` 指定配置文件；省略 `-i` 时各脚本从标准输入读取。

可以先用自带的虚构数据试运行（先复制配置并填写 `search_keywords`）：

```bash
cp config.example.json /tmp/sj-config.json
# 在 /tmp/sj-config.json 中填入 search_keywords，然后：
python3 scripts/filter_candidates.py -i examples/sample_candidates.json --config /tmp/sj-config.json > /tmp/kept.json
python3 scripts/format_digest.py -i /tmp/kept.json -o /tmp/digest.md
python3 scripts/validate_digest.py /tmp/digest.md
```

### 候选 JSON 字段

| 字段 | 说明 |
|---|---|
| `company` | 公司名称 |
| `job_title` | 广告中的完整正式岗位名称；无空缺补齐可用如 Company outreach (no open ad) |
| `ad_url` | 招聘广告的直接链接；无空缺补齐填 none，或配合 has_ad: false |
| `has_ad` | 可选布尔值；无空缺补齐设为 false |
| `website` | 公司官网 |
| `street_address` | 例如 Level 12, 100 Sample Street（会自动简化） |
| `suburb` | 例如 Melbourne CBD VIC 3000（会自动简化） |
| `headcount` | LinkedIn 人数区间，例如 1,001-5,000 |
| `lead_name`、`lead_title` | 一位合适的联系人及其职位 |
| `lead_linkedin` | 可选，LinkedIn 个人主页链接 |
| `lead_email` | 可选；仅在公开可查时填写，否则留空或填 none |

## 求职平台

只在以下平台进行**不登录**搜索：

- [SEEK](https://www.seek.com.au)
- [Indeed](https://au.indeed.com)
- [LinkedIn Jobs](https://www.linkedin.com/jobs)

AI 助手不会登录账号，也不会绕过验证码或反爬检查。

## 摘要格式

- 不编号。
- 每个岗位 3 个字段，字段之间空一行。
- 公司之间用两条 Markdown 分隔线（`---` 再 `---`）。

```
**Company** — Full official job title — [ad](url)

StreetNo StreetName StreetType, Suburb — headcount — [website](url)

Name — title — [LinkedIn](url) — email|none

---
---

**Next Company** — Company outreach (no open ad) — none
```

地址会自动简化：去掉门牌号前的 Level/Suite/Unit/Floor 和楼宇名称，去掉州名缩写和邮编，`Melbourne CBD` 显示为 `Melbourne`。人数区间显示为 `1001~5000`。

## Release 与安装包

每个打了标签的版本（例如 `v0.2.0`）都会在 GitHub 上有对应的 Release，包含：

- `searching-job-vX.Y.Z.zip`——可直接使用的安装包（`SKILL.md`、`scripts/`、`examples/`、`config.example.json`、两份 README、许可证）
- GitHub 自动生成的源代码压缩包

从 Release 安装：下载 zip 并解压，然后从 **初始化** 第 2 步开始操作。

维护者可以这样生成 zip：

```bash
git archive --format=zip --prefix=searching-job/ -o searching-job-v0.2.0.zip v0.2.0
```

## 基本原则

- 绝不编造：无法核实的信息宁可留空，也不猜测。
- 除非你明确要求，否则不会发送任何外联消息。
- 摘要只能由 `format_digest.py` 生成，并经 `validate_digest.py` 校验。
