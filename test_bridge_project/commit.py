try:
    from duggerlink.cli.commit import main
except ImportError:
    print("❌ DuggerLinkTools not found. Run: pip install -e C:\\Github\\DuggerLinkTools")
    exit(1)

if __name__ == "__main__":
    main()