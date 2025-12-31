"""
OpenRouter AI integration for content generation

Recommended model: google/gemini-2.5-flash:free
- Free tier available
- Fast response times
- Full vision support for image analysis
- Good quality for general content generation

See MODELS_INFO.md for detailed model comparison
"""
import aiohttp
import json
import base64
from typing import List, Dict, Any, Optional, Union


class AIGenerator:
    """
    OpenRouter AI content generator
    
    Supports:
    - Text generation (quotes, summaries)
    - Image analysis (book covers)
    - Vision-capable models (Gemini 2.5 Flash recommended)
    """
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize AI generator
        
        Args:
            api_key: OpenRouter API key
            model: Model name (e.g., 'google/gemini-2.5-flash:free')
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def generate_quotes(self, book_text: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Generate quotes from book text
        
        Args:
            book_text: Book text content
            count: Number of quotes to generate
        
        Returns:
            List of quote dictionaries with 'quote' and 'context' keys
        """
        prompt = f"""از متن کتاب زیر، {count} نقل‌قول برتر را استخراج کن که:
- الهام‌بخش و تاثیرگذار باشند
- مستقل و بدون نیاز به context قابل فهم باشند
- هر نقل‌قول حداکثر 2-3 جمله
- به زبان فارسی روان

متن کتاب:
{book_text[:8000]}

خروجی را فقط به صورت JSON بده:
[{{"quote": "...", "context": "..."}}, ...]"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"OpenRouter API error: {resp.status} - {error_text}")
                    
                    data = await resp.json()
                    content = data['choices'][0]['message']['content']
                    
                    # Extract JSON from response (might be wrapped in markdown)
                    content = content.strip()
                    if content.startswith('```'):
                        # Remove markdown code blocks
                        lines = content.split('\n')
                        content = '\n'.join(lines[1:-1])
                    
                    # Parse JSON
                    quotes = json.loads(content)
                    return quotes if isinstance(quotes, list) else []
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse quotes JSON: {str(e)}")
            return []
        except Exception as e:
            print(f"Error generating quotes: {str(e)}")
            return []
    
    async def generate_summary(self, book_text: str, min_words: int = 150, 
                              max_words: int = 300) -> Dict[str, Any]:
        """
        Generate book summary
        
        Args:
            book_text: Book text content
            min_words: Minimum words in summary
            max_words: Maximum words in summary
        
        Returns:
            Dictionary with 'summary', 'key_points', and 'genre'
        """
        prompt = f"""یک خلاصه جذاب {min_words}-{max_words} کلمه‌ای از این کتاب بنویس که:
- محتوای اصلی را منتقل کند
- زبان ساده و روان داشته باشد
- 3 نکته کلیدی را برجسته کند
- مخاطب را تشویق به مطالعه کند

متن کتاب:
{book_text[:10000]}

خروجی را به صورت JSON بده:
{{"summary": "...", "key_points": ["...", "...", "..."], "genre": "..."}}"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"OpenRouter API error: {resp.status} - {error_text}")
                    
                    data = await resp.json()
                    content = data['choices'][0]['message']['content']
                    
                    # Extract JSON from response
                    content = content.strip()
                    if content.startswith('```'):
                        lines = content.split('\n')
                        content = '\n'.join(lines[1:-1])
                    
                    # Parse JSON
                    summary = json.loads(content)
                    return summary if isinstance(summary, dict) else {}
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse summary JSON: {str(e)}")
            return {}
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return {}
    
    async def analyze_image(self, image_data: Union[bytes, str], 
                           prompt: Optional[str] = None,
                           vision_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze image using vision-capable model
        
        Args:
            image_data: Image as bytes or base64 string
            prompt: Custom prompt for image analysis (if None, uses default)
            vision_model: Vision model name (if None, uses default vision model)
        
        Returns:
            Dictionary with analysis results
        """
        # Use vision model if provided, otherwise try to use a vision-capable version
        model = vision_model or self.model
        
        # Default prompt for book cover analysis
        if not prompt:
            prompt = """این تصویر جلد یک کتاب است. لطفا اطلاعات زیر را استخراج کن:
- عنوان کتاب (اگر قابل خواندن است)
- نام نویسنده (اگر قابل خواندن است)
- دسته‌بندی/ژانر کتاب (بر اساس تصویر و طراحی جلد)
- توضیحات کوتاه درباره طراحی جلد
- پیشنهاد برای تگ‌های مناسب

خروجی را به صورت JSON بده:
{"title": "...", "author": "...", "category": "...", "cover_description": "...", "tags": ["...", "..."]}"""
        
        # Convert image to base64 if it's bytes
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{image_base64}"
        else:
            # Assume it's already base64 or a URL
            if image_data.startswith('http'):
                image_url = image_data
            else:
                image_url = f"data:image/jpeg;base64,{image_data}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": image_url
                                        }
                                    }
                                ]
                            }
                        ],
                        "temperature": 0.7
                    },
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"OpenRouter API error: {resp.status} - {error_text}")
                    
                    data = await resp.json()
                    content = data['choices'][0]['message']['content']
                    
                    # Extract JSON from response
                    content = content.strip()
                    if content.startswith('```'):
                        lines = content.split('\n')
                        content = '\n'.join(lines[1:-1])
                    
                    # Parse JSON
                    try:
                        analysis = json.loads(content)
                        return analysis if isinstance(analysis, dict) else {"description": content}
                    except json.JSONDecodeError:
                        # If not JSON, return as description
                        return {"description": content}
        
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return {"error": str(e)}
    
    async def generate_content_from_image(self, image_data: Union[bytes, str],
                                         content_type: str = "quote",
                                         book_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate content (quote, description, etc.) from book cover image
        
        Args:
            image_data: Image as bytes or base64 string
            content_type: Type of content to generate (quote, description, summary)
            book_title: Optional book title for context
        
        Returns:
            Generated content dictionary
        """
        prompts = {
            "quote": f"""با توجه به جلد این کتاب{' با عنوان ' + book_title if book_title else ''}، یک نقل‌قول الهام‌بخش و جذاب (2-3 جمله) که با موضوع کتاب مرتبط باشد، پیشنهاد بده.

خروجی JSON:
{{"quote": "...", "context": "..."}}""",
            
            "description": f"""یک توضیح جذاب و کوتاه (100-150 کلمه) برای معرفی این کتاب{' با عنوان ' + book_title if book_title else ''} بنویس که:
- مخاطب را جذب کند
- درباره موضوع کتاب اطلاعات بدهد
- زبان ساده و روان باشد

خروجی JSON:
{{"description": "...", "key_points": ["...", "..."]}}""",
            
            "summary": f"""با توجه به جلد و عنوان این کتاب{' (' + book_title + ')' if book_title else ''}، یک خلاصه کوتاه و جذاب (150-200 کلمه) درباره محتوای احتمالی کتاب بنویس.

خروجی JSON:
{{"summary": "...", "genre": "...", "target_audience": "..."}}"""
        }
        
        prompt = prompts.get(content_type, prompts["description"])
        
        return await self.analyze_image(image_data, prompt=prompt)
    
    async def generate_content_from_history(self, published_content_history: List[Dict[str, Any]], 
                                           content_type: str = "quote",
                                           book_title: Optional[str] = None,
                                           book_author: Optional[str] = None,
                                           book_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate content based on published content history to learn patterns
        
        Args:
            published_content_history: List of published content dictionaries with text/caption
            content_type: Type of content to generate (quote, description, summary)
            book_title: Book title
            book_author: Book author
        
        Returns:
            Generated content dictionary matching the pattern
        """
        # Extract patterns from history
        history_texts = []
        for content in published_content_history[:20]:  # Use last 20 posts
            text = content.get('text') or content.get('caption') or ''
            if text and len(text) > 20:  # Only meaningful content
                history_texts.append(text[:500])  # Limit length
        
        if not history_texts:
            # If no history, use default generation
            return await self._generate_default_content(content_type, book_title, book_author)
        
        # Create prompt based on history patterns with explicit anti-repetition instructions
        history_examples = "\n".join([f"- {text[:200]}" for text in history_texts[:5]])
        
        # Recent snippets to avoid
        recent_snippets = "\n".join([f"- {t[:80]}..." for t in history_texts[:5]])
        
        # Book text context for unique content
        book_context = ""
        if book_text and len(book_text) > 100:
            # Use middle section for variety (not always start)
            text_len = len(book_text)
            start_pos = text_len // 4  # Start from 25% into the text
            book_chunk = book_text[start_pos:start_pos+1500]
            book_context = f"\n\n**متن کتاب (برای استخراج محتوای منحصر به فرد):**\n{book_chunk}"
        
        book_info = f'"{book_title}"' if book_title else "این کتاب"
        if book_author:
            book_info += f" نوشته {book_author}"

        prompts = {
            "quote": f"""یک نقل‌قول کاملا جدید و منحصر به فرد از {book_info} استخراج کن.

{book_context}

**الگوی سبک نوشتاری قبلی (فقط برای سبک، نه برای محتوا):**
{history_examples}

**⚠️ مهم: از محتوای زیر استفاده نکن (تکراری است):**
{recent_snippets}

**نیازها:**
- نقل‌قول کاملا جدید و متفاوت از الگوهای بالا
- مستقیما از متن کتاب استخراج شده باشد
- الهام‌بخش و تاثیرگذار (2-3 جمله)
- سبک نوشتاری مشابه الگوهای بالا
- به زبان فارسی روان

خروجی JSON:
{{"quote": "...", "context": "توضیح کوتاه درباره نقل‌قول"}}""",
            
            "description": f"""یک معرفی جذاب و کاملا جدید برای {book_info} بنویس.

{book_context}

**الگوی سبک نوشتاری قبلی:**
{history_examples}

**⚠️ مهم: از محتوای زیر استفاده نکن:**
{recent_snippets}

**نیازها:**
- معرفی کاملا جدید و متفاوت
- 150-250 کلمه
- جذاب و تشویق‌کننده
- شامل نکات کلیدی کتاب
- سبک مشابه الگوهای بالا اما محتوای منحصر به فرد

خروجی JSON:
{{"description": "...", "key_points": ["نکته 1", "نکته 2", "نکته 3"]}}""",
            
            "summary": f"""یک خلاصه کاملا جدید و منحصر به فرد از {book_info} بنویس.

{book_context}

**الگوی سبک نوشتاری قبلی:**
{history_examples}

**⚠️ مهم: از محتوای زیر استفاده نکن:**
{recent_snippets}

**نیازها:**
- خلاصه کاملا جدید و متفاوت
- 200-300 کلمه
- شامل نکات کلیدی و اصلی کتاب
- جذاب و قابل فهم
- سبک مشابه الگوها اما محتوای منحصر به فرد

خروجی JSON:
{{"summary": "...", "key_points": ["نکته 1", "نکته 2", "نکته 3"], "genre": "ژانر کتاب"}}"""
        }
        
        prompt = prompts.get(content_type, prompts["description"])
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.9  # Higher temperature for more variety and creativity
                    },
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"OpenRouter API error: {resp.status} - {error_text}")
                    
                    data = await resp.json()
                    content = data['choices'][0]['message']['content']
                    
                    # Extract JSON from response
                    content = content.strip()
                    if content.startswith('```'):
                        lines = content.split('\n')
                        content = '\n'.join(lines[1:-1])
                    
                    # Parse JSON
                    result = json.loads(content)
                    return result if isinstance(result, dict) else {"error": "Invalid response format"}
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response JSON: {str(e)}")
            return {"error": f"Failed to parse response: {str(e)}"}
        except Exception as e:
            print(f"Error generating content from history: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_default_content(self, content_type: str, book_title: Optional[str], 
                                       book_author: Optional[str]) -> Dict[str, Any]:
        """Generate default content when no history is available"""
        title_text = f' "{book_title}"' if book_title else ''
        author_text = f' نوشته {book_author}' if book_author else ''
        
        if content_type == "quote":
            return {
                "quote": f"نقل‌قولی الهام‌بخش از کتاب{title_text}{author_text}",
                "context": "متن کتاب"
            }
        elif content_type == "description":
            return {
                "description": f"معرفی کتاب{title_text}{author_text}",
                "key_points": ["نکته 1", "نکته 2"]
            }
        else:
            return {
                "summary": f"خلاصه کتاب{title_text}{author_text}",
                "genre": "عمومی"
            }

