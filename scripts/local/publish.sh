SCRIPT_ROOT=$(dirname $(realpath "$0"))
echo -e '\nRunning publish.sh\n'

find . -name "dist" -exec rm -rf {} +
cd $SCRIPT_ROOT/../../src/ChatbotDemo.App
dotnet publish -c Release -r linux-x64 -p:Version=2.0.0.0 --no-self-contained -o $SCRIPT_ROOT/../../dist/release/publish/ChatbotDemo.App

echo -e '\nListing published files\n'
cd $SCRIPT_ROOT/../../dist/release/publish/ChatbotDemo.App
ls -la
