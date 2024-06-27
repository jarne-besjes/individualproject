
int rec(int i) {
    if (i == 1) {
        return 1;

    int x = 1;
    while (x < 5) {
        x = x + 1;
    }

    return rec( i- 1);
}


int main() {
    rec(5);
}