---
title: solo-opportunities — Product Card
doc_id: CARD-solo-opportunities
doc_type: product-card
verdict: showcase
version: 0.1
date: 2026-10-11
status: ร่างเพื่อพิจารณา
owner: Product owner (Book Dev)
---

# solo-opportunities — Product Card

## 1. สรุปคุณค่าในหนึ่งประโยค

ช่วยเจ้าของ Solo Empire เก็บโอกาสทางรายได้/ธุรกิจพร้อมสถานะ หน้าต่างเวลา และ action ที่ทำไปแล้ว ผ่าน API ของ cell เอง

## 2. ปัญหาและผู้ใช้เป้าหมาย

- ปัญหา: ตาราง opportunities เดิมอยู่ใน SQLite ส่วนกลาง
- ผู้ใช้: เจ้าของคนเดียว (internal)

## 3. สิ่งที่ทำได้จริงตอนนี้

- API `/v1/opportunities` (กรอง `type`, `status`, `window_status`) และ `/v1/opportunity-actions` (กรอง `category`, `action`)
- โฟลเดอร์ `docs/` เก็บงานวิจัยโอกาสเดิม (inventory, niche-research, market-trends, applications ฯลฯ) ที่ย้ายมาพร้อมประวัติ git — เป็นเอกสาร ไม่ใช่โค้ด
- ไม่มี publisher (ต่างจาก cell อื่นบางตัว)

## 4. หลักฐานสถานะ

| รายการ | ค่า (ตรวจจาก repository) |
|---|---|
| Stack | FastAPI, Python |
| Commits | 995 (แรก 2026-06-14 → ล่าสุด 2026-10-11) |
| Source | ประมาณ 2,841 บรรทัดใน 20 ไฟล์ (ไม่รวมเทสต์) |
| Tests | 3 ไฟล์ |
| CI | ไม่มี |
| Deploy config | Dockerfile + Railway (ตาม README); ไม่ได้ตรวจ deploy จริงในรอบนี้ |
| Live URL | ไม่มี (ไม่ได้ตรวจ) |
| README | 35 บรรทัด |

## 5. คุณค่าและจุดต่าง

- แยกเป็น 1 cell = 1 repo / 1 backend / 1 Neon database ตามแนว decentralize ของ Solo Empire; ใช้ identity, authorization, executions และ audit ของ `empire-platform` ผ่าน HTTP ด้วย token ของผู้เรียก ไม่เก็บ provider token เอง
- มุมรายได้: ไม่มี — เป็นโครงสร้างภายในของเจ้าของ แต่ pattern สร้าง cell จาก `cell.yaml` ด้วย `solo-cell-kit` ใช้ซ้ำได้ **[สมมติฐาน]**

## 6. ช่องว่างสำคัญ

- `cell.yaml` ระบุว่า cell นี้ว่างเปล่าตอนย้ายออกจาก control plane (2026-10-11) — ยังไม่มีข้อมูลจริงใน API
- commit 995 รายการส่วนใหญ่มาจากประวัติเอกสารที่ย้ายมา ไม่ใช่การพัฒนา cell
- ไม่มี CI

## 7. คำตัดสิน

**`showcase`** — Cell ว่างที่พร้อมใช้และคลังเอกสารวิจัยที่มีค่าเชิงข้อมูล แต่ยังไม่มีข้อมูลหรือผู้ใช้ จะเปลี่ยนเมื่อมีโอกาสถูกบันทึกผ่าน API จริง

## 8. ขั้นต่อไป

1. ตัดสินใจว่าจะนำเข้า `docs/` บางส่วนเป็นข้อมูลใน API หรือคงเป็นเอกสาร
2. เพิ่ม CI รัน `pytest`

## การอนุมัติ

| บทบาท | สถานะ | วันที่ | ลงนาม |
|---|---|---|---|
| Product owner (Book Dev) | รอพิจารณา | — | ________ |

## แหล่งข้อมูล

- `README.md`
- `cell.yaml`
- `tests/test_contract.py`, `migrations/`, `Dockerfile`
