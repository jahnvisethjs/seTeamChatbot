from typing import List, Dict, Optional, Tuple
import datetime
import re
import json
from langchain_core.messages import HumanMessage, SystemMessage

class OnboardingAssistant:
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        # Define the work constraints
        self.WORK_DAYS = ["Tuesday", "Wednesday", "Thursday", "Friday"]
        self.WORK_START_HOUR = 9
        self.WORK_END_HOUR = 17
        self.TARGET_WEEKLY_HOURS = 20
        # Track the last generated work schedule for agenda generation
        self.last_work_schedule = None
        
    def process_message(self, message: str, image_bytes: Optional[bytes] = None) -> str:
        """Process a message in onboarding mode."""
        message_lower = message.lower()
        
        # Check for agenda request first — even if an image is attached,
        # if the user mentions "agenda", route to agenda generation (with the image)
        if any(w in message_lower for w in ["agenda", "onboarding plan", "welcome packet"]):
            return self.generate_onboarding_agenda(message, image_bytes)

        # If an image is uploaded without agenda keywords, treat as class timetable → work schedule
        if image_bytes:
            result = self.generate_work_schedule(message, image_bytes)
            return result

        # Check for schedule/timetable related keywords → generate work schedule
        if any(w in message_lower for w in ["schedule", "timetable", "class", "calendar", "availability"]):
            result = self.generate_work_schedule(message, image_bytes)
            return result
            
        # Check for other onboarding keywords
        if any(w in message_lower for w in ["onboarding", "new joiner", "welcome"]):
            return self.generate_onboarding_agenda(message)
            
        return """I can help you with two main onboarding tasks:

**1 — Generate Work Schedule:**
Upload an image of your class timetable (or paste it as text), and I'll create a 20-hour work schedule (Tue-Fri, 9am-5pm) that fits around your classes.

**2 — Generate Onboarding Agenda:**
Once you have your work schedule, ask me to "generate an agenda" and I'll create a full 21-business-day onboarding plan fit to your working hours. You can also provide a work schedule directly (text or image) when requesting the agenda.

What would you like to do?"""

    def _extract_schedule_from_image(self, image_bytes: bytes) -> str:
        """Extract a human-readable work schedule from an uploaded image using the LLM."""
        import base64
        from io import BytesIO
        try:
            from PIL import Image
        except ImportError:
            Image = None

        # Process image — convert to PNG for maximum API compatibility
        if Image:
            try:
                img = Image.open(BytesIO(image_bytes))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                max_dim = 1024
                if max(img.width, img.height) > max_dim:
                    scale = max_dim / max(img.width, img.height)
                    new_size = (int(img.width * scale), int(img.height * scale))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_bytes = buffer.getvalue()
            except Exception as img_err:
                print(f"Image processing warning: {img_err}")

        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        extraction_prompt = """Look at this image of a work schedule. Extract the COMPLETE weekly work schedule.
Return a clean, human-readable summary in this exact format:

Weekly Work Schedule:
- Monday: [start time] - [end time] ([hours] hours) at [location] OR OFF
- Tuesday: [start time] - [end time] ([hours] hours) at [location] OR OFF
- Wednesday: [start time] - [end time] ([hours] hours) at [location] OR OFF
- Thursday: [start time] - [end time] ([hours] hours) at [location] OR OFF
- Friday: [start time] - [end time] ([hours] hours) at [location] OR OFF

Total Weekly Hours: [total]

Also note any special details visible in the schedule (e.g., remote days, specific room numbers, etc.).
If something is unclear, make your best interpretation and note it."""

        return self.rag_engine.llm.invoke_vision(extraction_prompt, image_base64)


    def generate_onboarding_agenda(self, message: str, image_bytes: Optional[bytes] = None) -> str:
        """Generate a comprehensive 21-business-day onboarding agenda based on the user's request."""
        # Use LLM to generate the agenda
        if not self.rag_engine.llm:
            return "I need access to the AI model to generate agendas. Please check your API token."

        # If an image was uploaded, extract the work schedule from it first
        extracted_schedule = ""
        if image_bytes:
            try:
                extracted_schedule = self._extract_schedule_from_image(image_bytes)
                print(f"DEBUG: Extracted schedule from image: {extracted_schedule[:300]}...")
            except Exception as e:
                print(f"Warning: Could not extract schedule from image: {e}")
                extracted_schedule = "(Could not extract schedule from image — please provide it as text.)"
        
        # If no image and no extracted schedule, check if we have a previously generated work schedule
        if not extracted_schedule and self.last_work_schedule:
            extracted_schedule = self.last_work_schedule
            print(f"DEBUG: Using previously generated work schedule for agenda")

        # Load the agenda template for context
        template_context = ""
        import os
        template_path = os.path.join("data", "onboarding_agenda_template.md")
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_context = f.read()
            except Exception:
                pass

        # Build the schedule constraint section
        schedule_section = ""
        if extracted_schedule:
            schedule_section = f"""
## WORK SCHEDULE CONSTRAINT (EXTRACTED FROM UPLOADED IMAGE)
The following work schedule was extracted from the image the user uploaded.
You MUST use these exact working hours for the "Weekly Regular Work Schedule" table
and ensure ALL day-by-day activities fit WITHIN these time windows.
Do NOT schedule any activities outside these hours on any day.
If a day is marked as OFF, mark it as OFF in the agenda too.

{extracted_schedule}

IMPORTANT: Each day's schedule table should start at the shift start time and end at the shift end time shown above.
Activities (check-ins, meetings, work blocks, reflections) must be time-blocked within these hours.
"""

        system_prompt = f"""You are an expert HR Onboarding Specialist for the Office of University Affairs at Arizona State University.
Your task is to create a COMPREHENSIVE, FULL onboarding agenda for a new joiner on the SE (Systems Engineering) team.

CRITICAL: The agenda MUST span 21 business days (approximately 4 weeks, Monday-Friday). This is NOT a short summary — it is a detailed, day-by-day schedule with time-blocked activities.
{schedule_section}
## REFERENCE TEMPLATE
Use this template as the structural guide for the agenda:

{template_context}

## REQUIRED STRUCTURE

### SECTION 1: COVER PAGE
Include:
- **Onboarding Agenda** header with the current semester/year
- Name, Role, Email (use [email]@asu.edu placeholder if not given), Phone
- **Additional Resources**: Shared Google Drive, Workday HCM FAQs, Weekly SE student team schedule
- **Independent Work Items** checklist (complete list with sub-items):
  - Foundations in Community Engaged Practices modules (Self-care, Ethics, Equitable communication, Democracy, Process/Product/Participatory Publics)
  - Work+ Pathways
  - Explore ASU Briefing Materials
  - ASU online training modules via Workday (Intro to Workday, Time Tracking and Reporting, ASU Information Security Training, Fire Safety, Title IX Training, ASU Inclusive Communities, Arizona Public Service Policy, Preventing Harassment and Discrimination Training, Seeds of Sustainability)

### SECTION 2: WEEKLY SCHEDULE & TABLE OF CONTENTS
- Weekly Regular Work Schedule table (Mon-Fri with Start shift, End shift, Hours, Location)
- Table of Contents listing ALL 21 business days with dates

### SECTION 3: DAY-BY-DAY SCHEDULES (21 business days)
Each day MUST be a markdown table with columns: **Time** | **Activity** | **Who** | **Location**

**Day 1 activities MUST include:**
- Arrive at Fulton Center (with address: 300 E University Dr, Tempe, AZ 85281)
- Intro meeting with supervisor (review agenda, confirm hiring items, discuss professional development, weekly checkouts, Workday hours)
- Complete tasks: Draft professional bio, Complete Read Me, Review onboarding schedule, Add contact info to team directory, Set up ASU email signature, Watch training videos
- Discussion: Day 1 reflections
- End-of-day reflection questions

**Days 2-5 (Week 1) activities include:**
- Daily check-in with supervisor (15 min)
- Independent Work Unstructured Time (complete checklist items)
- Overview: Collaboratory + ASU SE interns
- Weekly Collaboratory Standup meeting
- Debrief Collaboratory next steps
- Set up technology (Microsoft Outlook, Slack, Zoom, Google Workspace, Asana)
- Intro to Collaboratory and Proxying
- Proxy Activities
- Dev Setup (Docker, shell scripts, local environment)
- Daily end-of-day reflection questions
- Daily checkout meeting/reflections

**Days 6-10 (Week 2) activities include:**
- Daily check-ins
- Proxy Activities based on feedback from Pavan
- Use Proxy AI and write improvements and general thoughts
- Data curation for Collaboratory Activities
- Review evaluation documents (ProxyAI_Response_Evaluation, GeneralProxying_Response_Evaluation)
- Continue independent work items
- Weekly Collaboratory Standup meeting
- Daily reflections and checkouts

**Days 11-15 (Week 3) activities include:**
- Increasing independent work time
- Intro to first project: Test Cases Documentation
- Continue proxy activities with more autonomy
- Collaboratory data curation contributions
- Weekly Collaboratory Standup meeting
- Daily reflections and checkouts

**Days 16-21 (Week 4) activities include:**
- Primary focus on independent project work
- Test cases document work
- Proxy activities based on accumulated feedback
- Data curation contributions
- Daily reflections and checkouts
- 30-day end-of-onboarding reflection on the final day

## RECURRING DAILY ACTIVITIES
Every working day should include these recurring elements:
1. **Check-in with Supervisor** (15 min, start of day): Address questions, set daily priorities
2. **Independent Work Time** (1-2 hrs): Complete checklist items or structured project work
3. **End-of-day reflection questions** (30 min): Fostering communication and improvement
4. **Checkout meeting/reflections** (30 min, end of day): Share thoughts, feelings, questions
5. **Break** (15-30 min, mid-afternoon)

## ROLE-SPECIFIC ADJUSTMENTS
- **Software Development Analyst (SDA)**: Emphasize dev setup (Docker, shell scripts), Proxy AI activities, Test Cases Documentation, Collaboratory platform work, data curation
- **Management Intern**: Emphasize community engagement data, spatial data analysis, HR/admin modules, Community Engaged Practices, ASU Briefing Materials

## KEY TEAM MEMBERS (use these for the "Who" column):
- MS (Mani) - Manikandan Sundararaman (Supervisor)
- AV (Aakash) - Aakash Vashishtha (Team Lead)
- CN (Christina) - Christina Nawrocki (Office Director)
- Julia - Team member
- DP (Dragos) - IT/Dev support
- PM (Pavan) - Collaboratory/Proxy mentor
- Salvador, Kristin - Collaboratory stakeholders

## LOCATIONS
- Fulton Center - 300 E University Dr, Tempe, AZ 85281
- Fulton 245 - Student workspace
- Fulton 2451 - Meeting room
- Fulton 2489 - Supervisor office
- CN office - Christina's office

## FORMATTING RULES
- Use clean Markdown formatting
- Each day should have its own header (e.g., "### Monday, [Date]")
- Use markdown tables for daily schedules
- Mark OFF days clearly
- Mark CN OOO (Christina Out Of Office) days where applicable (typically first few days)
- Include the purpose/description for each activity
- If the user provides a name, use it throughout. Otherwise use [Name] as placeholder.
- If the user provides a start date, calculate actual dates for all 21 days
- If no start date is given, use "Day 1", "Day 2", etc.
- Generate the COMPLETE agenda — do NOT summarize or abbreviate any days."""

        try:
            user_content = f"Generate a complete 21-business-day onboarding agenda based on this request: {message}"
            if extracted_schedule:
                if image_bytes:
                    source_label = "extracted from the uploaded image"
                elif self.last_work_schedule and extracted_schedule == self.last_work_schedule:
                    source_label = "generated from the previous class timetable analysis"
                else:
                    source_label = "provided"
                user_content += f"\n\nThe work schedule ({source_label}) is:\n{extracted_schedule}"

            response = self.rag_engine.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_content)
            ])
            return response
        except Exception as e:
            return f"Error generating agenda: {str(e)}"

    def generate_work_schedule(self, message: str, image_bytes: Optional[bytes] = None) -> str:
        """Parse class schedule and generate a work schedule."""
        if not self.rag_engine.llm:
            return "I need access to the AI model to parse your schedule. Please check your API token."

        import base64
        from io import BytesIO
        try:
            from PIL import Image
        except ImportError:
            Image = None

        # Step 1: Parse the class schedule using LLM
        parsing_prompt = """
        Extract the class schedule from the provided input (text or image).
        Return ONLY a raw JSON list of objects. No markdown formatting, no explanations.
        Each object must have:
        - "day": one of ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        - "start_time": "HH:MM" (24-hour format)
        - "end_time": "HH:MM" (24-hour format)
        
        If a day has multiple classes, list them as separate objects.
        Input text:
        """ + message

        try:
            if image_bytes:
                # Process image — convert to PNG for maximum API compatibility
                if Image:
                    try:
                        img = Image.open(BytesIO(image_bytes))
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        max_dim = 1024
                        if max(img.width, img.height) > max_dim:
                            scale = max_dim / max(img.width, img.height)
                            new_size = (int(img.width * scale), int(img.height * scale))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                        buffer = BytesIO()
                        img.save(buffer, format="PNG")
                        image_bytes = buffer.getvalue()
                    except Exception as img_err:
                        print(f"Image processing warning: {img_err}")

                # Use invoke_vision for image-based schedule parsing
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                json_response = self.rag_engine.llm.invoke_vision(parsing_prompt, image_base64)
            else:
                json_response = self.rag_engine.llm.invoke(parsing_prompt)

            
            if not json_response or not str(json_response).strip():
                return "The AI returned an empty response. This might be due to a safety filter or an issue reading the provided input. Please try again or paste the text directly."

            # Robust JSON extraction
            json_response_str = str(json_response).strip()
            
            # Strategy 1: Look for JSON blocks
            json_str = ""
            start_index = json_response_str.find('[')
            end_index = json_response_str.rfind(']')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = json_response_str[start_index:end_index+1]
            else:
                # Strategy 2: Clean triple backticks
                json_str = json_response_str
                if "```" in json_str:
                    # Extract content between triple backticks
                    blocks = re.findall(r'```(?:json)?\s*(.*?)```', json_str, re.DOTALL)
                    if blocks:
                        json_str = blocks[0].strip()
            
            if not json_str:
                return f"I couldn't find a schedule in the AI's response. It said: \"{json_response_str}\". Please try providing the schedule in a clearer format."

            class_slots = json.loads(json_str)
        except Exception as e:
            msg = "I couldn't understand the class schedule."
            if image_bytes:
                msg += " Please try providing a clearer image or paste the schedule as text."
            else:
                msg += " Please try pasting it again in a clear format (e.g., 'Mon 10:00-11:30, Wed 14:00-15:30')."
            
            # Add the raw response to help with debugging if it's not too long
            raw_preview = str(json_response)[:200] + "..." if len(str(json_response)) > 200 else str(json_response)
            return f"{msg}\n\n**Error:** {str(e)}\n**AI Response Preview:** {raw_preview}"

        # Step 2: Calculate work slots
        work_slots = self._calculate_work_slots(class_slots)
        
        if not work_slots:
            return """I couldn't find a valid schedule that meets the 20-hour requirement within the constraints. Please check your class schedule for conflicts.

**Constraints applied:**
- 📆 Working days: **Tuesday – Friday** only
- ⏰ Working hours: **9:00 AM – 5:00 PM**
- 🔄 Single shift per day (no split shifts)
- 🚶 15-minute buffer after each class (travel time to Fulton Center)
- 🎯 Target: **20 hours/week**"""

        # Step 3: Format the output using LLM for natural presentation
        response = "### 📅 Proposed Work Schedule\n\n"
        response += "Based on your class timetable, here is a work schedule that avoids all your classes and meets the requirements:\n\n"
        response += "**Constraints applied:**\n"
        response += "- 📆 Working days: Tuesday – Friday only\n"
        response += "- ⏰ Working hours: 9:00 AM – 5:00 PM\n"
        response += "- 🔄 Single shift per day (no split shifts)\n"
        response += "- 🚶 15-minute travel buffer after each class ends\n"
        response += "- 📍 Location: Fulton 245 (300 E University Dr, Tempe, AZ 85281)\n"
        response += "- 🎯 Target: 20 hours/week\n\n"
        
        response += "#### Weekly Work Schedule\n\n"
        response += "| Day | Start | End | Hours | Location |\n"
        response += "|-----|-------|-----|-------|----------|\n"
        
        total_hours = 0
        for day in self.WORK_DAYS:
            if day in work_slots:
                start, end = work_slots[day]
                hours = (datetime.datetime.strptime(end, "%H:%M") - datetime.datetime.strptime(start, "%H:%M")).seconds / 3600
                total_hours += hours
                # Format times for display (e.g., 09:00 -> 9:00 AM)
                start_dt = datetime.datetime.strptime(start, "%H:%M")
                end_dt = datetime.datetime.strptime(end, "%H:%M")
                try:
                    start_display = start_dt.strftime("%I:%M %p").lstrip("0")
                    end_display = end_dt.strftime("%I:%M %p").lstrip("0")
                except Exception:
                    start_display = start
                    end_display = end
                response += f"| **{day}** | {start_display} | {end_display} | {hours:.1f} | Fulton 245 |\n"
            else:
                response += f"| **{day}** | — | — | 0.0 | — |\n"
        
        response += f"\n**Total Weekly Hours: {total_hours:.1f}**\n"
        
        if total_hours < 20:
            response += f"\n⚠️ *Note: Only {total_hours:.1f} hours could be scheduled due to class conflicts. The target is 20 hours/week.*\n"
        
        # Show the parsed class schedule for verification
        response += "\n---\n#### 📚 Your Class Schedule (as parsed)\n\n"
        for slot in sorted(class_slots, key=lambda x: (["Monday","Tuesday","Wednesday","Thursday","Friday"].index(x['day']) if x['day'] in ["Monday","Tuesday","Wednesday","Thursday","Friday"] else 5, x['start_time'])):
            response += f"- **{slot['day']}**: {slot['start_time']} – {slot['end_time']}\n"
        
        # Save the work schedule for potential agenda generation
        schedule_summary = "Weekly Work Schedule:\n"
        for day in self.WORK_DAYS:
            if day in work_slots:
                start, end = work_slots[day]
                hours = (datetime.datetime.strptime(end, "%H:%M") - datetime.datetime.strptime(start, "%H:%M")).seconds / 3600
                schedule_summary += f"- {day}: {start} - {end} ({hours:.1f} hours) at Fulton 245\n"
            else:
                schedule_summary += f"- {day}: OFF\n"
        schedule_summary += f"Total Weekly Hours: {total_hours:.1f}"
        self.last_work_schedule = schedule_summary
        
        response += "\n---\n💡 **Next step:** Say **\"generate agenda\"** and I'll create a full 21-business-day onboarding plan based on this work schedule!\n"
        
        return response

    def _calculate_work_slots(self, class_slots: List[Dict]) -> Optional[Dict[str, Tuple[str, str]]]:
        """
        Calculate work slots based on constraints:
        - Tue-Fri only
        - 9am - 5pm (09:00 - 17:00)
        - Single shift per day
        - Total 20 hours
        - 15-minute buffer before AND after classes for commute to/from Fulton Center
        """
        # Initialize busy intervals for work days
        busy_intervals = {day: [] for day in self.WORK_DAYS}
        
        # Populate busy intervals from class schedule
        for slot in class_slots:
            day = slot['day']
            if day in self.WORK_DAYS:
                start = self._time_to_minutes(slot['start_time'])
                end = self._time_to_minutes(slot['end_time'])
                # Add 15-minute buffer BEFORE class (need to leave work to travel to class)
                # and 15-minute buffer AFTER class (travel back to Fulton Center)
                busy_start = max(start - 15, self._time_to_minutes("09:00"))
                busy_end = end + 15
                busy_intervals[day].append((busy_start, busy_end))
        
        # Define work window in minutes (9am=540, 5pm=1020)
        work_start = self._time_to_minutes("09:00")
        work_end = self._time_to_minutes("17:00")
        
        daily_availability = {}
        
        for day in self.WORK_DAYS:
            # Sort and merge busy intervals if they overlap
            intervals = sorted(busy_intervals[day])
            merged = []
            if intervals:
                curr_start, curr_end = intervals[0]
                for next_start, next_end in intervals[1:]:
                    if next_start <= curr_end:
                        curr_end = max(curr_end, next_end)
                    else:
                        merged.append((curr_start, curr_end))
                        curr_start, curr_end = next_start, next_end
                merged.append((curr_start, curr_end))
            
            # Find free blocks
            free_blocks = []
            current_cursor = work_start
            
            for start, end in merged:
                if start > current_cursor:
                    free_blocks.append((current_cursor, start))
                current_cursor = max(current_cursor, end)
            
            if current_cursor < work_end:
                free_blocks.append((current_cursor, work_end))
            
            # Keep only the largest block for "single shift" rule
            if free_blocks:
                largest_block = max(free_blocks, key=lambda x: x[1] - x[0])
                daily_availability[day] = largest_block
            else:
                daily_availability[day] = (0, 0) # No availability

        total_minutes_needed = 1200 # 20 hours
        
        # Check if we have enough total capacity
        total_capacity = sum((end - start) for start, end in daily_availability.values())
        if total_capacity < total_minutes_needed:
            # Try to return the best we can if at least some hours are available
            if total_capacity > 0:
                total_minutes_needed = total_capacity  # Use max available
            else:
                return None # Truly impossible
            
        # Target 5 hours (300 mins) per day
        allocation = {day: 0 for day in self.WORK_DAYS}
        remaining_needed = total_minutes_needed
        
        # First pass: Allocate up to 5 hours where possible
        for day in self.WORK_DAYS:
            avl_start, avl_end = daily_availability[day]
            avl_duration = avl_end - avl_start
            
            alloc = min(avl_duration, 300)
            allocation[day] = alloc
            remaining_needed -= alloc
        
        # Second pass: If we need more (someone had < 5h), take from others who have space
        if remaining_needed > 0:
            for day in self.WORK_DAYS:
                if remaining_needed <= 0: break
                
                avl_start, avl_end = daily_availability[day]
                avl_duration = avl_end - avl_start
                current_alloc = allocation[day]
                
                can_add = avl_duration - current_alloc
                if can_add > 0:
                    add_amount = min(can_add, remaining_needed)
                    allocation[day] += add_amount
                    remaining_needed -= add_amount
            
        # Construct schedule
        final_schedule = {}
        for day in self.WORK_DAYS:
            alloc = allocation[day]
            if alloc > 0:
                avl_start, avl_end = daily_availability[day]
                # Start as early as possible within the largest block
                # The block boundaries already account for the 15m buffers
                shift_start = avl_start
                shift_end = shift_start + alloc
                final_schedule[day] = (self._minutes_to_time(shift_start), self._minutes_to_time(shift_end))
                
        return final_schedule

    def _time_to_minutes(self, time_str: str) -> int:
        try:
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        except:
            return 0

    def _minutes_to_time(self, minutes: int) -> str:
        h = minutes // 60
        m = minutes % 60
        return f"{h:02d}:{m:02d}"
