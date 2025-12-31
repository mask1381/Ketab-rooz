"""
مثال استفاده از تحلیل عکس با OpenRouter AI

این فایل نشان می‌دهد چطور از قابلیت تحلیل عکس استفاده کنید.
"""

import asyncio
from core.ai_generator import AIGenerator
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL


async def example_analyze_image():
    """مثال تحلیل عکس جلد کتاب"""
    
    # Initialize AI generator
    ai = AIGenerator(OPENROUTER_API_KEY, OPENROUTER_MODEL)
    
    # خواندن عکس از فایل
    with open('path/to/book_cover.jpg', 'rb') as f:
        image_data = f.read()
    
    # تحلیل عکس با پرامپ پیش‌فرض
    result = await ai.analyze_image(image_data)
    print("نتایج تحلیل:")
    print(result)
    
    # تحلیل عکس با پرامپ سفارشی
    custom_prompt = """این جلد کتاب را تحلیل کن و بگو:
    - چه رنگ‌هایی استفاده شده؟
    - چه احساسی به بیننده می‌دهد؟
    - برای چه گروه سنی مناسب است؟"""
    
    result = await ai.analyze_image(image_data, prompt=custom_prompt)
    print("\nنتایج تحلیل سفارشی:")
    print(result)


async def example_generate_content_from_image():
    """مثال تولید محتوا از عکس جلد"""
    
    ai = AIGenerator(OPENROUTER_API_KEY, OPENROUTER_MODEL)
    
    # خواندن عکس
    with open('path/to/book_cover.jpg', 'rb') as f:
        image_data = f.read()
    
    # تولید نقل‌قول
    quote_result = await ai.generate_content_from_image(
        image_data,
        content_type="quote",
        book_title="کتاب نمونه"
    )
    print("نقل‌قول تولید شده:")
    print(quote_result)
    
    # تولید توضیحات
    desc_result = await ai.generate_content_from_image(
        image_data,
        content_type="description",
        book_title="کتاب نمونه"
    )
    print("\nتوضیحات تولید شده:")
    print(desc_result)


# نحوه استفاده:
# asyncio.run(example_analyze_image())
# asyncio.run(example_generate_content_from_image())


