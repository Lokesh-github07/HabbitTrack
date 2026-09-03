@echo off

echo Building latest HabbitTrack image...
docker build -t habbittrack .

echo Stopping old container...
docker rm -f habbittrack-container 2>nul

echo Starting updated container...
docker run -d --name habbittrack-container -p 5000:5000 habbittrack

echo.
echo HabbitTrack is running at http://localhost:5000
pause