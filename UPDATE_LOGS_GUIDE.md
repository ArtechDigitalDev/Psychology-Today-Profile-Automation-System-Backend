# Update Logs সিস্টেম গাইড

## **Update Logs কি?**

`update_logs` টেবিল হল একটি **বিস্তারিত লগিং সিস্টেম** যা প্রতিটি প্রোফাইল মেইনটেনেন্স অ্যাক্টিভিটির সম্পূর্ণ তথ্য রেকর্ড করে।

## **টেবিল স্ট্রাকচার**

### **update_logs টেবিল**

| কলাম | টাইপ | বর্ণনা |
|------|------|--------|
| `log_id` | `int` | প্রাইমারি কী |
| `profile_id` | `int` | প্রোফাইল ID (ফরেন কী) |
| `executed_at` | `timestamp` | কখন রান হয়েছে |
| `outcome` | `varchar(20)` | ফলাফল (Success/Failure/Warning) |
| `duration_ms` | `int` | কত সময় লাগেছে (মিলিসেকেন্ড) |
| `fields_edited` | `json` | কোন ফিল্ড আপডেট হয়েছে |
| `log_details` | `text` | বিস্তারিত তথ্য/এরর মেসেজ |

## **API এন্ডপয়েন্ট**

### **1. সব লগ দেখুন**
```bash
GET /api/update-logs/
Authorization: Bearer <your_token>
```

**উদাহরণ রেসপন্স:**
```json
{
  "success": true,
  "message": "Update logs retrieved successfully.",
  "data": [
    {
      "log_id": 1,
      "profile_id": 1,
      "executed_at": "2024-01-15T14:00:00Z",
      "outcome": "Success",
      "duration_ms": 5000,
      "fields_edited": {
        "headline": "Compassionate Therapist - john_therapist",
        "specialties": "Anxiety, Depression, Trauma"
      },
      "log_details": "Profile john_therapist maintenance completed successfully"
    }
  ]
}
```

### **2. নির্দিষ্ট প্রোফাইলের লগ**
```bash
GET /api/update-logs/profile/{profile_id}
Authorization: Bearer <your_token>
```

### **3. ফলাফল অনুযায়ী লগ**
```bash
GET /api/update-logs/outcome/Success
GET /api/update-logs/outcome/Failure
GET /api/update-logs/outcome/Warning
Authorization: Bearer <your_token>
```

### **4. লগ সামারি**
```bash
GET /api/update-logs/summary?days=7
Authorization: Bearer <your_token>
```

**উদাহরণ রেসপন্স:**
```json
{
  "success": true,
  "message": "Update logs summary for last 7 days retrieved successfully.",
  "data": {
    "total_logs": 15,
    "success_count": 12,
    "failure_count": 2,
    "warning_count": 1,
    "average_duration_ms": 4500.5,
    "recent_logs": [...]
  }
}
```

### **5. স্ট্যাটিসটিক্স**
```bash
GET /api/update-logs/stats
Authorization: Bearer <your_token>
```

**উদাহরণ রেসপন্স:**
```json
{
  "success": true,
  "message": "Update logs statistics retrieved successfully.",
  "data": {
    "total_logs": 150,
    "success_count": 120,
    "failure_count": 25,
    "warning_count": 5,
    "success_rate_percentage": 80.0,
    "average_duration_ms": 4200.0,
    "profile_stats": {
      "1": {"total": 10, "success": 8, "failure": 2},
      "2": {"total": 15, "success": 12, "failure": 3}
    }
  }
}
```

## **অটোমেশন লগ**

### **অটোমেশন API দিয়ে লগ দেখুন**
```bash
GET /api/automation/logs
Authorization: Bearer <your_token>
```

**উদাহরণ রেসপন্স:**
```json
{
  "success": true,
  "message": "Automation logs retrieved successfully.",
  "data": {
    "logs": [
      {
        "timestamp": "2024-01-15T14:00:00Z",
        "level": "INFO",
        "message": "Profile john_therapist maintenance completed successfully",
        "profile_id": 1,
        "duration_ms": 5000,
        "outcome": "Success"
      },
      {
        "timestamp": "2024-01-15T14:05:00Z",
        "level": "ERROR",
        "message": "Profile jane_counselor login failed",
        "profile_id": 2,
        "duration_ms": 2000,
        "outcome": "Failure"
      }
    ]
  }
}
```

## **লগ ডাটা উদাহরণ**

### **সফল রান**
```json
{
  "log_id": 1,
  "profile_id": 1,
  "executed_at": "2024-01-15T14:00:00Z",
  "outcome": "Success",
  "duration_ms": 5000,
  "fields_edited": {
    "headline": "Compassionate Therapist - john_therapist",
    "specialties": "Anxiety, Depression, Trauma, Relationship Issues",
    "summary": "Experienced therapist providing compassionate care",
    "approaches": "CBT, DBT, EMDR, Person-Centered Therapy",
    "client_focus": "Adults, Adolescents, Couples"
  },
  "log_details": "Profile john_therapist maintenance completed successfully"
}
```

### **ব্যর্থ রান**
```json
{
  "log_id": 2,
  "profile_id": 2,
  "executed_at": "2024-01-15T14:05:00Z",
  "outcome": "Failure",
  "duration_ms": 2000,
  "fields_edited": null,
  "log_details": "Error processing profile jane_counselor: Invalid credentials"
}
```

## **লগ ট্র্যাকিং প্রসেস**

### **অটোমেশন চলার সময়**
```python
# 1. শুরু করার সময়
start_time = time.time()

# 2. প্রসেসিং
success = self.run_profile_automation(profile, password, ai_content)

# 3. সময় গণনা
duration_ms = int((time.time() - start_time) * 1000)

# 4. লগ তৈরি
if success:
    UpdateLog.create_log(
        db=self.db,
        profile_id=profile.profile_id,
        outcome="Success",
        duration_ms=duration_ms,
        fields_edited=ai_content,
        log_details=f"Profile {profile.pt_username} maintenance completed successfully"
    )
else:
    UpdateLog.create_log(
        db=self.db,
        profile_id=profile.profile_id,
        outcome="Failure",
        duration_ms=duration_ms,
        log_details=f"Profile {profile.pt_username} maintenance failed"
    )
```

## **মনিটরিং এবং অ্যানালিটিক্স**

### **সাকসেস রেট ট্র্যাকিং**
```python
# সাকসেস রেট গণনা
success_rate = (success_count / total_logs * 100)
```

### **পারফরমেন্স ট্র্যাকিং**
```python
# গড় সময় গণনা
average_duration_ms = sum(durations) / len(durations)
```

### **প্রোফাইল-ভিত্তিক স্ট্যাটস**
```python
# প্রতিটি প্রোফাইলের স্ট্যাটস
profile_stats = {
    "1": {"total": 10, "success": 8, "failure": 2},
    "2": {"total": 15, "success": 12, "failure": 3}
}
```

## **সেটআপ**

### **1. টেবিল তৈরি**
```bash
python create_tables.py
```

### **2. অটোমেশন শুরু**
```bash
POST /api/automation/start
```

### **3. লগ চেক**
```bash
GET /api/update-logs/
```

## **সুবিধা**

### **1. বিস্তারিত ট্র্যাকিং**
- প্রতিটি অ্যাকশনের সম্পূর্ণ তথ্য
- সময় ট্র্যাকিং
- এরর ডিটেইলস

### **2. পারফরমেন্স মনিটরিং**
- গড় সময় গণনা
- সাকসেস রেট ট্র্যাকিং
- বটলনেক চিহ্নিতকরণ

### **3. ডিবাগিং**
- এরর কারণ খুঁজে বের করা
- সমস্যাযুক্ত প্রোফাইল চিহ্নিতকরণ
- ট্রেন্ড অ্যানালাইসিস

### **4. রিপোর্টিং**
- সাপ্তাহিক/মাসিক রিপোর্ট
- স্ট্যাটিসটিক্স
- অ্যানালিটিক্স

## **ফিউচার এনহ্যান্সমেন্ট**

### **পরিকল্পিত ফিচার**
- **ইমেইল অ্যালার্ট**: ব্যর্থ রান নোটিফিকেশন
- **ড্যাশবোর্ড**: রিয়েল-টাইম মনিটরিং
- **অ্যানালিটিক্স**: ট্রেন্ড অ্যানালাইসিস
- **অটো-রিপোর্ট**: সাপ্তাহিক/মাসিক রিপোর্ট

**সুতরাং `update_logs` টেবিল হল আপনার অটোমেশন সিস্টেমের "মেমরি" - যা সব কিছু রেকর্ড করে এবং ভবিষ্যতে অ্যানালাইসিস করার জন্য ডাটা সেভ করে রাখে!** 