# شرح المشروع (قالب عام لـ AWS) — بالعربية

هذا المشروع أصبح **قالب (Template) عام واحترافي** لبناء خدمات على AWS.

## 1) ماذا يفعل القالب؟
- **Lambda + API Gateway (HTTP API)**: مناسب للـ APIs السريعة والطلبات القصيرة.
- **ECS Fargate**: مناسب للحاويات (Containers) والعمليات الطويلة أو التي تحتاج بيئة ثابتة.

تم تعديل الكود بحيث **كل Lambda / API / ECS يعمل بدون قواعد بيانات أو إعدادات خاصة**، ويكتفي بـ `print` و `return`ردود بسيطة.

## 2) أهم التعديلات التي تمت
- حذف أي معلومات حساسة (كلمات مرور / IDs / معلومات VPC و RDS) من الملفات.
- تحديث اسم الخدمة إلى: `aws-microservices-template`.
- تبسيط الـ endpoints:
  - `GET /api/health`
  - `GET/POST /api/echo`
  - `GET /api/private/me` (مثال فقط — بدون تحقق JWT حقيقي)
  - `GET /print` (Lambda تطبع الحدث في CloudWatch)
- جعل الاتصال بقاعدة البيانات اختياري:
  - إذا لم تضع `DB_URL` → يستخدم SQLite في الذاكرة (بدون أخطاء)

## 3) أفضل تصميم على AWS (سريع وآمن)
### هل أعمل خدمة واحدة أم عدة خدمات؟
**الأفضل عادة: Microservices**
- كل خدمة في حاوية مستقلة (أو Lambda مستقلة) عندما:
  - عندك فرق مختلفة لكل جزء
  - تريد نشر (Deploy) مستقل لكل خدمة
  - تريد عزل الصلاحيات (IAM) لكل خدمة

**خدمة واحدة (Monolith) ممكن** عندما:
- المشروع صغير أو MVP
- تريد تقليل التكلفة والتعقيد

### متى أستخدم Lambda ومتى ECS؟
- استخدم **Lambda** لـ:
  - CRUD APIs
  - Webhooks
  - معالجة خفيفة وسريعة
- استخدم **ECS/Fargate** لـ:
  - عمليات طويلة (أكثر من حدود Lambda)
  - خدمات WebSockets أو Background workers
  - متطلبات مكتبات/نظام تشغيل خاص

## 4) كيف أجعل الـ API سريع؟
- تفعيل **Caching** (CloudFront أو API Gateway caching)
- تقليل حجم الاستجابة (JSON صغير)
- استخدام **Provisioned Concurrency** لـ Lambda إذا هناك برود/Cold start
- وضع ECS خلف **ALB** وتفعيل Auto Scaling

## 5) كيف أجعل المشروع آمن؟
- مبدأ **Least Privilege** في IAM: كل خدمة تحصل على أقل صلاحيات ممكنة
- لا تضع أسرار في الملفات:
  - استخدم **Secrets Manager** أو **SSM Parameter Store**
- إضافة **WAF** أمام API Gateway أو ALB
- تفعيل **Rate limiting** (Usage Plans أو WAF rules)
- Logs + Tracing:
  - CloudWatch Logs
  - AWS X-Ray (اختياري)

## 6) طريقة النشر المقترحة
### Serverless (Lambda)
- ملف: `serverless.yml` جاهز كقالب.
- ضع القيم عبر `--stage` و variables أو عبر CI/CD.

### CDK (ECS)
- داخل `infra/cdk` يوجد Stack عام.
- افتراضياً ينشئ VPC جديد.
- إذا عندك VPC جاهز، فعّل `useExistingVpc=true` و مرّر الـ IDs.

## 7) ملاحظات مهمة
- هذا القالب مقصود أن يكون **عام**، لذلك تركنا ميزات متقدمة كـ Cognito/JWT و RDS و S3 كـ "اختياري".
- عندك نقطة ممتازة: الأفضل أن كل خدمة تكون مستقلة (Container/Lambda) مع CI/CD ومراقبة.

---

إذا أردت، أقدر أضيف أيضاً:
- GitHub Actions أو CodePipeline جاهز
- WAF + CloudFront
- تقسيم الخدمات إلى 3–5 services نموذجية (auth, users, orders, ...)


## ملاحظة مهمة (نسخة V2)
- في هذه النسخة **أبقينا إعدادات VPC/Subnets/Security Groups داخل** `serverless.yml` و `infra/cdk/cdk.json`
  مع قيم **Placeholder** (مثل `vpc-0123...` و `subnet-...` و `sg-...`).  
  عند النشر الحقيقي لازم تستبدلها بقيمك الفعلية أو تجعلها تُقرأ من Secrets/SSM/CI variables.

## ما معنى SQLite in-memory؟
عندما لا يتوفر `DB_URL` (يعني ما عندك قاعدة بيانات مُهيأة بعد):
- التطبيق يستخدم **SQLite داخل الذاكرة**: `sqlite:///:memory:`
- هذا يُفيد كـ **Fallback للتشغيل/الاختبار** بدون أي إعدادات.
- البيانات **لا تُحفظ**: بمجرد أن تنتهي عملية الـ Lambda أو الحاوية، تختفي الجداول والبيانات.
- الهدف: منع انهيار الخدمة وتمكينك من اختبار الـ API بسرعة، ثم لاحقًا تستبدلها بقاعدة فعلية عبر `DB_URL`.
