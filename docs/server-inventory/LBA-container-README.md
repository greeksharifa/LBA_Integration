<!--
Source: /home/ywjang/LBA/README.md
Preserved on 2026-10-22 from a container-level file outside any Git repository.
This is a provenance snapshot; current branch ownership is documented in the
LBA_Integration README and /home/ywjang/LBA/README.md when available.
-->

# LBA container README snapshot

The following content is copied verbatim from `/home/ywjang/LBA/README.md`.

---

# LBA

Learning by Asking 연구에 사용하는 저장소와 실험 코드를 모아 둔다.

| 경로 | 내용 |
| --- | --- |
| `LBA_LAVIS/` | LAVIS 기반 LBA 모델과 원격 실험 branch |
| `LBA_Integration/` | 기관별 LBA 통합 코드와 연도별 branch |
| `IG-VLM_LBA/` | IG-VLM 기반 LBA 실험 |
| `Flipped-VQA/` | 보존 중인 `greeksharifa/Flipped-VQA` fork checkout; `LBA_LAVIS` checkout이 아님 |
| `DramaQA/` | DramaQA 외부 코드 |
| `archivers/` | 원격 branch에 반영된 이전 checkout과 로컬 전용 결과·모델·데이터 보존본 |

## Canonical branch map

| 저장소 / branch | 역할 |
| --- | --- |
| `LBA_Integration:demo/legacy-institution-pipeline` | sanitize된 legacy 기관 서비스 contract와 client orchestration |
| `LBA_LAVIS:inquirer/data-export-pipeline` | sanitize된 INQUIRER data export pipeline |
| `LBA_LAVIS:inquirer/flipped-vqa-augmentation` | data export branch 위의 Flipped-VQA augmentation |
| `greeksharifa/Flipped-VQA:master` | `mlvlab/Flipped-VQA`의 기존 fork로 그대로 보존 |

`/home/ywjang/kbs/Flipped-VQA`는 로컬 artifact 전용 workspace다.
`/home/ywjang/LBA/Flipped-VQA`도 `greeksharifa/Flipped-VQA` fork의 local
checkout이며, 두 경로 모두 `LBA_LAVIS` 또는 위 INQUIRER branch의
canonical 위치로 취급하지 않는다.

`LBA_LAVIS_uncertainty_v2`의 전체 로컬 checkout은 `archivers/LBA_LAVIS_uncertainty_v2/`에 보존한다. `LBA_Uv2`는 해당 보존본을 가리키는 상대 경로 별칭이다. `json_schema.md`는 실험 데이터 형식 참고 문서다.

일부 스크립트와 가상환경에는 이전 위치의 절대 경로가 남아 있다. 실행하기 전에 데이터·모델·출력 경로를 현재 환경에 맞게 설정한다.

중복 checkout의 재사용 가능한 tracked 변경은 각 canonical 저장소의 의미별 원격 branch에 보존한다. 이전 `greeksharifa/LBA_Prototypes`의 source head와 분류는 `LBA_Integration/docs/provenance/LBA_Prototypes-inventory.md`에 기록되어 있으며 해당 원격은 publication 전에 이미 존재하지 않았다. 원격에 올리지 않는 실행 결과와 실험 상태는 `archivers/` 아래의 원래 checkout에 함께 보존한다.
