# HabitTrack - Habit Tracking Made Easy

A modern, full-stack habit tracking application with authentication, analytics, and social sharing features.

## Features

### Tracker View (Calendar Grid Format)
- **Calendar Grid**: View and manage habits in a table format similar to Excel
  - Left column: Habit names
  - Top row: Days of the week with dates
  - Grid cells: Checkboxes for daily completion
- **14-Day View**: Track habits across two weeks at a time
- **Navigation**: Move between periods with Previous/Next buttons
- **Add Habits**: Create new habits with names
- **Quick Actions**: Edit or delete habits directly from the table

### Analytics View
Multiple visualization types to track your progress:

1. **Pie Chart (Doughnut)**: Completion rate distribution across all habits
2. **Line Chart**: Weekly completion trends for each habit
3. **Bar Chart**: Total completions per habit
4. **Contribution Table**: 12-week heatmap showing daily activity levels
5. **Statistics Summary**:
   - Total Completions
   - Average Completion Rate
   - Best Performing Habit
   - Current Streak (consecutive days with all habits completed)

## How to Use

### Getting Started

1. Open `index.html` in your web browser
2. The app will load with no habits by default

### Creating Habits

1. Go to the **Tracker** view (default)
2. Enter a habit name in the input field (e.g., "Exercise", "Read", "Meditate")
3. Click **Add Habit** or press Enter
4. The habit will appear as a new row in the calendar grid

### Tracking Habits

1. Each habit row shows 14 days across the top (2 weeks of dates)
2. Click the checkbox for each day to mark the habit as completed
3. The checkboxes show a green checkmark when completed
4. Use the week navigation buttons to view and manage past/future weeks

### Editing/Deleting Habits

1. Click on the habit name or the **✎** (Edit) button to open the edit modal
2. You can:
   - **Edit**: Update the habit emoji and name
   - **Save**: Save your changes
   - **Delete**: Permanently remove the habit
   - **Cancel**: Close without changes

### Viewing Analytics

1. Click the **Analytics** button in the sidebar
2. View multiple chart types:
   - **Pie Chart**: Shows completion rate for each habit
   - **Line Chart**: Displays daily trends for the past week
   - **Bar Chart**: Compares total completions between habits
   - **Contribution Table**: Heat map of activity over 12 weeks
3. **Statistics Cards** show:
   - Total completions across all habits
   - Average completion rate
   - Your best performing habit
   - Current streak length

## Data Storage

- All data is saved locally in your browser's LocalStorage
- Data persists between sessions
- Clearing browser cache will delete your data

## Calendar Layout

The tracker uses a spreadsheet-style layout:
- **DAILY HABITS** header on the left
- Days of the week displayed horizontally across the top
- Habit names with emojis in the left column
- Checkbox grid for tracking daily completions
- Quick action buttons on the right (Edit/Delete)

## Color Scheme

- **Primary**: Indigo (#6366f1)
- **Success**: Green (#10b981)
- **Danger**: Red (#ef4444)
- **Completion Levels**: Green gradient (light to dark)

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- No backend server required
- Responsive design for mobile and tablet devices

## Technical Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js
- **Storage**: Browser LocalStorage API
- **Responsive Design**: Mobile-friendly layout

## Tips for Best Results

1. **Be Consistent**: Check off habits daily for better statistics
2. **Use Meaningful Names**: Make habit names clear and specific
3. **Choose Recognizable Emojis**: Use emojis that visually represent your habit
4. **Keep it Simple**: Start with 3-5 habits for easier tracking
5. **Review Weekly**: Check the analytics view weekly to identify patterns
6. **Set Realistic Goals**: Aim for 5-7 completions per week per habit

## File Structure

```
HabbitTrack/
├── index.html      # Main HTML structure with calendar grid
├── styles.css      # Styling and responsive design
├── app.js          # Application logic and data management
└── README.md       # This file
```

## Future Enhancements

Possible features to add:
- Category/Tags for habits
- Habit frequency settings (daily, weekdays, weekends, etc.)
- Reminders and notifications
- Export data as CSV/PDF
- Import from other tracking apps
- Dark mode
- Cloud sync
- Mobile app version
- Habit notes/comments
- Habit streaks and milestones

## Keyboard Shortcuts

- **Enter**: Add new habit from input field
- **Click habit name**: Edit habit
- **Click emoji**: Show edit modal

## License

Free to use for personal habit tracking

---

**Created with 💜 for better habits**
