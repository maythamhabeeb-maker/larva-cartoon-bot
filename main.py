"""main.py — تشغيل Pipeline من سطر الأوامر (للاختبار)."""
import sys
from pipeline import cartoon_pipeline


def main():
    idea = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if not idea:
        idea = input("أدخل فكرة القصة: ").strip()

    print(f"\n🎬 بدء إنتاج: «{idea}»\n" + "─" * 40)
    video = cartoon_pipeline.run(idea=idea)
    print(f"\n✅ الفيديو النهائي: {video}")


if __name__ == "__main__":
    main()
