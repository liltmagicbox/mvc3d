# 02. 프레임 포맷 (바이트 헤더)

**결론: 매 프레임 경로(핫패스)는 고정 struct 헤더 + numpy 원시 바이트.
JSON은 SCHEMA/EVENT(콜드패스) 봉투에서만 허용.** 헤더를 만지는 코드는
`frame.py` 한 파일에만 존재한다.

근거 (N=1000, pos+quat f32, `python -m procsim.bench_format`):
크기 x5.2 (28KB vs 146KB), pack x466 (0.007ms vs 3.3ms), unpack x729.
JSON은 60fps 예산의 1/3을 직렬화에 태운다.

## 스펙 (리틀엔디언, 오프셋 고정)

```
FrameHeader 32B
  0  magic       4s   'MVS1'
  4  version     u8
  5  msg_type    u8   1=STATE  2=SCHEMA  3=EVENT
  6  section_n   u16
  8  frame_id    u32  단조증가 (스킵/중복/역행 감지 근거)
  12 payload_len u32  "정확히 이만큼 recv"의 근거
  16 sim_time    f64  생산 시각 perf_counter (지연·보간·클록보정에 사용)
  24 (예약)      8B

STATE payload = section_n x [SectionHeader 16B + raw bytes]
  0  kind      u32   드로우 배치 id (meshid '00010001' → 0x00010001)
  4  count     u32   인스턴스 수
  8  dtype     u8    0=f32 1=f16 2=i32 3=u32 4=u8 5=i16 6=u16 7=f64
  9  comps     u8    3=pos 4=quat 7=pos+quat 16=mat4
  10 flags     u16   (예약)
  12 byte_len  u32
  raw = count*comps*itemsize, numpy C-order

SCHEMA/EVENT payload = UTF-8 JSON
```

## 가이드

```python
from procsim import frame as fr

# 송신
blob = fr.pack_state(frame_id, sim_time, [(kind, pos_f32), (kind2, quat_f32)])
n = fr.pack_state_into(shm_buf, frame_id, sim_time, sections)  # 무복사(shm용)
hello = fr.pack_json(fr.SCHEMA, 0, 0.0, {'kinds': {...}})       # 콜드패스

# 수신
f = fr.unpack(blob)              # STATE: f.sections = [(kind, ndarray 뷰)]
for kind, arr in f.sections:     # arr.shape = (count, comps), 파싱비용 0
    glBufferSubData(..., arr)
# 버퍼가 재사용되는 경로(shm 슬롯)면 fr.unpack(blob, copy=True)

fr.meshid_to_kind('00010001')    # ↔ fr.kind_to_meshid(kind)
```

## 규칙

- **섹션 = 인스턴스드 드로우 배치 하나.** viewmodel의 ViewTable과 1:1.
- 정적/저빈도 데이터(메쉬 등록, 이름, 텍스처 경로)는 SCHEMA로 접속 시 1회.
- dtype에 f16(코드 1)이 있다 — 다이어트는 `arr.astype('float16')`로 끝.
- 수신은 `payload_len`만큼 정확히 읽는다(socklink.recv_exact) —
  START/END 마커, `}{` 경계 사고 계열 원천 봉쇄.
