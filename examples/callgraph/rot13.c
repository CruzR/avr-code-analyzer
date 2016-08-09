#include <stdio.h>
#include <ctype.h>

int rot13(int c)
{
	if (!isalpha(c)) return c;

	int base = (c >= 'a') ? 'a' : 'A';
	return base + ((c - base + 13) % 26);
}

int main(int argc, char *argv[])
{
	int i;
	char *p;

	for (i = 0; i < argc; ++i)
	{
		p = argv[i];

		while (*p)
		{
			*p = rot13(*p);
			++p;
		}

		puts(argv[i]);
	}

	return 0;
}
