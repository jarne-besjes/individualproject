
int rec(int i) {
    if (i == 1) {
        return 1;
}

    return rec( i- 1);
}


int main() {
    rec(5);
}