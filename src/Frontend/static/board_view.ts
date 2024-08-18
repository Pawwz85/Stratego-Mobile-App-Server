
const defaultBoardRsc = {
    dotSvg: '<svg height="800px" width="800px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 31.955 31.955" xml:space="preserve"> <g> <path style="fill:#030104;" d="M27.25,4.655C20.996-1.571,10.88-1.546,4.656,4.706C-1.571,10.96-1.548,21.076,4.705,27.3 c6.256,6.226,16.374,6.203,22.597-0.051C33.526,20.995,33.505,10.878,27.25,4.655z"/> <path style="fill:#030104;" d="M13.288,23.896l-1.768,5.207c2.567,0.829,5.331,0.886,7.926,0.17l-0.665-5.416 C17.01,24.487,15.067,24.5,13.288,23.896z M8.12,13.122l-5.645-0.859c-0.741,2.666-0.666,5.514,0.225,8.143l5.491-1.375 C7.452,17.138,7.426,15.029,8.12,13.122z M28.763,11.333l-4.965,1.675c0.798,2.106,0.716,4.468-0.247,6.522l5.351,0.672 C29.827,17.319,29.78,14.193,28.763,11.333z M11.394,2.883l1.018,5.528c2.027-0.954,4.356-1.05,6.442-0.288l1.583-5.137 C17.523,1.94,14.328,1.906,11.394,2.883z"/> <circle style="fill:#030104;" cx="15.979" cy="15.977" r="6.117"/> </g> </svg>',
    attackDotSvg: '<svg height="800px" width="800px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 31.955 31.955" xml:space="preserve"> <g> <path style="fill:#030104;" d="M27.25,4.655C20.996-1.571,10.88-1.546,4.656,4.706C-1.571,10.96-1.548,21.076,4.705,27.3 c6.256,6.226,16.374,6.203,22.597-0.051C33.526,20.995,33.505,10.878,27.25,4.655z"/> <path style="fill:#030104;" d="M13.288,23.896l-1.768,5.207c2.567,0.829,5.331,0.886,7.926,0.17l-0.665-5.416 C17.01,24.487,15.067,24.5,13.288,23.896z M8.12,13.122l-5.645-0.859c-0.741,2.666-0.666,5.514,0.225,8.143l5.491-1.375 C7.452,17.138,7.426,15.029,8.12,13.122z M28.763,11.333l-4.965,1.675c0.798,2.106,0.716,4.468-0.247,6.522l5.351,0.672 C29.827,17.319,29.78,14.193,28.763,11.333z M11.394,2.883l1.018,5.528c2.027-0.954,4.356-1.05,6.442-0.288l1.583-5.137 C17.523,1.94,14.328,1.906,11.394,2.883z"/> <circle style="fill:#030104;" cx="15.979" cy="15.977" r="6.117"/> </g> </svg>',
    soldierSvg: '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="800px" height="800px" viewBox="0 0 512 512"  xml:space="preserve"> <g> <path class="st0" d="M449.085,464.424c0,0-5.672-45.109-8.797-51.563c-2.813-5.75-92.75-50.375-112.063-61.563l-0.578,0.203 v-25.609c7.203-7.656,13.859-17.016,19.281-28.563c1.141-2.438,1.938-5.047,2.703-7.906c1.141-4.266,2.094-8.922,2.781-12.578 c0.016-0.063,0.016-0.109,0.031-0.172c3.094-0.75,5.906-2.172,8.313-3.891c5.375-3.922,9.281-9.328,12.453-14.984 c3.141-5.672,5.484-11.656,7.031-16.953c1.172-4.047,1.75-7.688,1.766-11.078c0-3.641-0.719-7.063-2.219-9.969 c-1.125-2.188-2.672-4.031-4.344-5.438c-0.203-0.156-0.406-0.266-0.594-0.422l-0.781-31.438 c7.531-6.422,10.313-14.719,10.313-20.484c0-7.453,0-18.078,0-29.781c0-15.938-11.25-21.281-20.984-23.359 c1,2.609,1.5,5.359,1.5,8.078c0,3.203-0.688,6.422-2.047,9.422c-7.266-14.047-49.781-96.188-57.719-110.359 c-10.188-18.219-41.734-23.531-56.609-1.922c-15.844,23.016-33.953,53.688-36.234,61.375l12.172-48.344 c-13.078-6.203-30.5-1.922-34.813,9.016c-3.25,8.297-33.891,79.75-39.391,92.563c-0.031-0.031-0.063-0.063-0.078-0.109 c-1.703-3.297-2.578-6.891-2.578-10.5c0-2.75,0.516-5.5,1.516-8.141v-0.016c0,0,0.172-0.391,0.453-1.141 c-9.828,2-21.359,7.281-21.359,23.438c0,11.703,0,22.328,0,29.781c0,5.781,2.797,14.094,10.344,20.516l-0.781,31.422 c-1.625,1.25-3.156,2.813-4.328,4.781c-1.891,3.125-2.844,6.938-2.828,11.031c0,3.391,0.609,7.031,1.781,11.078 c2.078,7.078,5.484,15.344,10.469,22.484c2.5,3.547,5.406,6.844,9.016,9.453c2.391,1.719,5.203,3.141,8.313,3.891 c0.234,1.266,0.5,2.656,0.813,4.109c0.563,2.781,1.234,5.797,2,8.641c0.781,2.859,1.563,5.469,2.703,7.906 c5.25,11.188,11.688,20.313,18.641,27.844v26.328l-0.578-0.203c-19.313,11.188-109.25,55.813-112.047,61.563 c-3.141,6.453-8.813,51.563-8.813,51.563c-1.484,7.422,0.25,15.141,4.766,21.203c4.531,6.078,11.406,9.953,18.953,10.656 c0,0,42.672,15.719,169.375,15.719c126.688,0,169.359-15.719,169.359-15.719c7.547-0.703,14.438-4.578,18.953-10.656 C448.851,479.564,450.569,471.846,449.085,464.424z M98.866,425.955l-6.75-12.531l59.078-30.829l7.703,12.844L98.866,425.955z M256.007,485.33c-5.75,0-10.422-4.656-10.422-10.406s4.672-10.406,10.422-10.406s10.406,4.656,10.406,10.406 S261.757,485.33,256.007,485.33z M256.007,421.768c-5.75,0-10.422-4.656-10.422-10.422c0-5.75,4.672-10.407,10.422-10.407 s10.406,4.656,10.406,10.407C266.413,417.111,261.757,421.768,256.007,421.768z M278.866,338.361 c-10.453,3.266-19.188,3.844-22.547,3.844c-2.234,0-6.891-0.25-12.813-1.391c-8.906-1.719-20.672-5.422-32.219-13.063 c-11.547-7.656-22.906-19.172-31.375-37.109c-0.406-0.813-1.109-2.906-1.75-5.281c-0.953-3.609-1.875-8-2.5-11.438 c-0.344-1.703-0.594-3.188-0.781-4.25c-0.078-0.516-0.156-0.922-0.203-1.219l-0.063-0.406l-1.219-7.688l-7.688,1.156l-0.703,0.047 c-1.078,0-2.281-0.344-3.969-1.547c-2.484-1.734-5.469-5.438-7.891-9.844c-2.453-4.406-4.453-9.484-5.672-13.719 c-0.859-2.953-1.141-5.188-1.141-6.688c0-1.641,0.297-2.406,0.469-2.781l0.438-0.547c0.266-0.219,0.781-0.5,1.625-0.719 c0.813-0.203,1.875-0.313,2.813-0.313c0.75,0,1.406,0.063,1.844,0.109l0.469,0.063l8.688,1.734 c0.172,0.328,0.344,0.609,0.516,0.953c0.016-0.266,0.063-0.547,0.094-0.828l0.094,0.016v-0.891c0.859-8.047,2.391-21.031,3.703-32 c28.766,8.641,74.672,20.5,74.672,20.5c9.469,2.844,19.625,2.844,29.078,0c0,0,45.953-11.859,74.719-20.516 c1.313,10.984,2.828,23.969,3.703,32.016v0.891l0.109-0.016c0.016,0.281,0.047,0.563,0.063,0.828 c0.188-0.328,0.359-0.625,0.516-0.938l8.719-1.75l0,0c0.234-0.031,1.188-0.172,2.281-0.172c0.844,0,1.766,0.078,2.531,0.25 c0.578,0.125,1.063,0.297,1.391,0.469c0.531,0.266,0.672,0.422,0.875,0.734c0.188,0.328,0.547,1.047,0.563,2.906 c0,1.5-0.281,3.734-1.141,6.688c-1.625,5.656-4.656,12.766-8.25,17.844c-1.781,2.547-3.688,4.547-5.328,5.719 c-1.688,1.203-2.891,1.547-3.953,1.547l-0.703-0.047l-7.703-1.156l-1.219,7.688l-0.031,0.172 c-0.141,0.953-0.875,5.453-1.922,10.375c-0.531,2.453-1.109,5.016-1.719,7.219c-0.578,2.172-1.25,4.078-1.609,4.828 c-5.656,11.969-12.594,21.047-20.016,28.063C301.616,329.22,289.366,335.095,278.866,338.361z M370.929,466.658h-13.984h-5.344 v5.344v13.984l-7-6.578l-7,6.578v-13.984v-5.344h-5.344h-13.969l6.578-7l-6.578-6.984h13.969h5.344v-5.359v-13.969l7,6.563l7-6.563 v13.969v5.359h5.344h13.984l-6.578,6.984L370.929,466.658z M413.147,425.955l-60.031-30.516l7.703-12.844l59.078,30.829 L413.147,425.955z"/> </g> </svg>',
    spySvg: '<svg width="800px" height="800px" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="#000000" d="M218 19c-1 0-2.76.52-5.502 3.107-2.742 2.589-6.006 7.021-9.191 12.76-6.37 11.478-12.527 28.033-17.666 45.653-4.33 14.844-7.91 30.457-10.616 44.601 54.351 24.019 107.599 24.019 161.95 0-2.706-14.144-6.286-29.757-10.616-44.601-5.139-17.62-11.295-34.175-17.666-45.653-3.185-5.739-6.45-10.171-9.191-12.76C296.76 19.52 295 19 294 19c-6.5 0-9.092 1.375-10.822 2.85-1.73 1.474-3.02 3.81-4.358 7.34-1.338 3.53-2.397 8.024-5.55 12.783C270.116 46.73 263.367 51 256 51c-7.433 0-14.24-4.195-17.455-8.988-3.214-4.794-4.26-9.335-5.576-12.881-1.316-3.546-2.575-5.867-4.254-7.315C227.035 20.37 224.5 19 218 19zm-46.111 124.334c-1.41 9.278-2.296 17.16-2.57 22.602 6.61 5.087 17.736 10.007 31.742 13.302C217.18 183.031 236.6 185 256 185s38.82-1.969 54.94-5.762c14.005-3.295 25.13-8.215 31.742-13.302-.275-5.443-1.161-13.324-2.57-22.602-55.757 23.332-112.467 23.332-168.223 0zM151.945 155.1c-19.206 3.36-36.706 7.385-51.918 11.63-19.879 5.548-35.905 11.489-46.545 16.57-5.32 2.542-9.312 4.915-11.494 6.57-.37.28-.247.306-.445.546.333.677.82 1.456 1.73 2.479 1.973 2.216 5.564 4.992 10.627 7.744 10.127 5.504 25.944 10.958 45.725 15.506C139.187 225.24 194.703 231 256 231s116.813-5.76 156.375-14.855c19.78-4.548 35.598-10.002 45.725-15.506 5.063-2.752 8.653-5.528 10.627-7.744.91-1.023 1.397-1.802 1.73-2.479-.198-.24-.075-.266-.445-.547-2.182-1.654-6.174-4.027-11.494-6.568-10.64-5.082-26.666-11.023-46.545-16.57-15.212-4.246-32.712-8.272-51.918-11.631.608 5.787.945 10.866.945 14.9v3.729l-2.637 2.634c-10.121 10.122-25.422 16.191-43.302 20.399C297.18 200.969 276.6 203 256 203s-41.18-2.031-59.06-6.238c-17.881-4.208-33.182-10.277-43.303-20.399L151 173.73V170c0-4.034.337-9.113.945-14.9zm1.094 88.205C154.558 308.17 200.64 359 256 359c55.36 0 101.442-50.83 102.96-115.695a748.452 748.452 0 0 1-19.284 2.013c-1.33 5.252-6.884 25.248-15.676 30.682-13.61 8.412-34.006 7.756-48 0-7.986-4.426-14.865-19.196-18.064-27.012-.648.002-1.287.012-1.936.012-.65 0-1.288-.01-1.936-.012-3.2 7.816-10.078 22.586-18.064 27.012-13.994 7.756-34.39 8.412-48 0-8.792-5.434-14.346-25.43-15.676-30.682a748.452 748.452 0 0 1-19.285-2.013zM137.4 267.209c-47.432 13.23-77.243 32.253-113.546 61.082 42.575 4.442 67.486 21.318 101.265 48.719l16.928 13.732-21.686 2.211c-13.663 1.393-28.446 8.622-39.3 17.3-5.925 4.738-10.178 10.06-12.957 14.356 44.68 5.864 73.463 10.086 98.011 20.147 18.603 7.624 34.81 18.89 53.737 35.781l5.304-23.576c-1.838-9.734-4.134-19.884-6.879-30.3-5.12-7.23-9.698-14.866-13.136-22.007C201.612 397.326 199 391 199 384c0-3.283.936-6.396 2.428-9.133a480.414 480.414 0 0 0-6.942-16.863c-29.083-19.498-50.217-52.359-57.086-90.795zm237.2 0c-6.87 38.436-28.003 71.297-57.086 90.795a480.521 480.521 0 0 0-6.942 16.861c1.493 2.737 2.428 5.851 2.428 9.135 0 7-2.612 13.326-6.14 20.654-3.44 7.142-8.019 14.78-13.14 22.01-2.778 10.547-5.099 20.82-6.949 30.666l5.14 23.42c19.03-17.01 35.293-28.338 53.974-35.994 24.548-10.06 53.33-14.283 98.011-20.147-2.78-4.297-7.032-9.618-12.957-14.355-10.854-8.679-25.637-15.908-39.3-17.3l-21.686-2.212 16.928-13.732c33.779-27.4 58.69-44.277 101.265-48.719-36.303-28.829-66.114-47.851-113.546-61.082zM256 377c-8 0-19.592.098-28.234 1.826-4.321.864-7.8 2.222-9.393 3.324-1.592 1.103-1.373.85-1.373 1.85s1.388 6.674 4.36 12.846c2.971 6.172 7.247 13.32 11.964 19.924 4.717 6.604 9.925 12.699 14.465 16.806 4.075 3.687 7.842 5.121 8.211 5.377.37-.256 4.136-1.69 8.21-5.377 4.54-4.107 9.749-10.202 14.466-16.806 4.717-6.605 8.993-13.752 11.965-19.924C293.612 390.674 295 385 295 384s.22-.747-1.373-1.85c-1.593-1.102-5.072-2.46-9.393-3.324C275.592 377.098 264 377 256 377zm0 61.953c-.042.03-.051.047 0 .047s.042-.018 0-.047zm-11.648 14.701L235.047 495h41.56l-9.058-41.285C264.162 455.71 260.449 457 256 457c-4.492 0-8.235-1.316-11.648-3.346z"/></svg>',
    flagSvg: '<svg fill="#000000" width="800px" height="800px" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg"> <title>flag</title> <path d="M0 30.016q0 0.832 0.576 1.408t1.44 0.576 1.408-0.576 0.576-1.408v-28q0-0.832-0.576-1.408t-1.408-0.608-1.44 0.608-0.576 1.408v28zM6.016 18.016h9.984v4h16l-4-8 4-8h-12v-4h-13.984v16zM10.016 14.016v-8h5.984v8h-5.984zM20 18.016v-8h5.536l-2.016 4 2.016 4h-5.536z"></path> </svg>',
    bombSvg: '<svg width="800px" height="800px" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--emojione-monotone" preserveAspectRatio="xMidYMid meet"><path d="M41.245 11.293c-.981.966-1.961 1.934-2.94 2.9c-.862.852.475 2.172 1.336 1.32c.981-.967 1.961-1.934 2.939-2.902c.865-.851-.475-2.171-1.335-1.318" fill="#000000"></path><path d="M46.761 8.486l2.91-2.873c.862-.852-.475-2.172-1.337-1.32l-2.911 2.873c-.864.854.473 2.173 1.338 1.32" fill="#000000"></path><path d="M48.334 15.514c.862.852 2.199-.469 1.337-1.32c-.981-.967-1.958-1.935-2.94-2.9c-.859-.853-2.199.467-1.337 1.318l2.94 2.902" fill="#000000"></path><path d="M41.215 8.486c.865.853 2.203-.467 1.34-1.318c-.971-.959-1.941-1.917-2.914-2.875c-.861-.853-2.198.469-1.336 1.32l2.91 2.873" fill="#000000"></path><path d="M44.934 16.904v-2.889c0-1.204-1.893-1.204-1.893 0v2.889c0 1.203 1.893 1.203 1.893 0" fill="#000000"></path><path d="M44.934 5.751V2.902c0-1.203-1.893-1.203-1.893 0v2.849c0 1.204 1.893 1.204 1.893 0" fill="#000000"></path><path d="M48.174 10.837h2.905c1.221 0 1.221-1.866 0-1.866h-2.905c-1.219 0-1.219 1.866 0 1.866" fill="#000000"></path><path d="M32.832 18.229A22.243 22.243 0 0 0 20.45 21.96l-3.778-3.731l-2.254 2.224c-2.295-2.496-4.403-5.648-3.122-7.889c2.564-4.49 16.702-4.402 28.327-1.748l.429-1.826C27.66 6.158 12.791 6.127 9.641 11.644c-1.509 2.64-.353 6.049 3.431 10.138l-2.409 2.377l3.779 3.73a21.604 21.604 0 0 0-3.779 12.226C10.663 52.2 20.589 62 32.832 62C45.078 62 55 52.2 55 40.114c0-12.088-9.922-21.885-22.168-21.885" fill="#000000"></path></svg>',
    minerSvg: '<svg width="800px" height="800px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"> <path fill-rule="evenodd" clip-rule="evenodd" d="M3.02172 1.79241C3.11977 1.33042 3.52766 1 3.99994 1H7.49994C10.8167 1 13.9504 2.15662 16.5142 4.05499L16.8139 3.77241C17.2074 3.40139 17.8246 3.41046 18.207 3.79289L20.207 5.79289C20.5895 6.17532 20.5986 6.79251 20.2275 7.18601L19.945 7.48571C21.8433 10.0496 22.9999 13.1833 22.9999 16.5V20C22.9999 20.4723 22.6695 20.8802 22.2075 20.9782C21.7455 21.0763 21.2779 20.8377 21.0861 20.4061C19.5548 16.9607 17.8884 14.1436 15.9191 11.7594L5.78873 22.5551C4.82264 23.5847 3.19624 23.6105 2.19791 22.6122L1.38775 21.802C0.389428 20.8037 0.415275 19.1773 1.44482 18.2112L12.2405 8.08084C9.85633 6.11151 7.03927 4.44513 3.5938 2.91381C3.16223 2.722 2.92368 2.2544 3.02172 1.79241ZM13.7415 9.41504L2.81338 19.6696C2.60747 19.8629 2.6023 20.1881 2.80197 20.3878L3.61213 21.198C3.81179 21.3976 4.13707 21.3925 4.33029 21.1866L14.5849 10.2585C14.3099 9.97106 14.0289 9.69005 13.7415 9.41504ZM8.31869 3.02736C10.6049 4.30007 12.6125 5.70113 14.4033 7.30303C15.2115 8.026 15.9739 8.78848 16.6969 9.59669C18.2988 11.3875 19.6999 13.3951 20.9726 15.6813C20.7848 12.8712 19.6408 10.2169 17.8574 8.06282C17.2794 7.36462 16.6353 6.72057 15.9371 6.14252C13.783 4.35913 11.1287 3.21514 8.31869 3.02736Z" fill="#000000"/> </svg>',
    scoutSvg: '<svg fill="#000000" height="800px" width="800px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512" xml:space="preserve"> <g> <g> <path d="M482.16,342.756l-14.324-80.909c2.8,0,5.07-2.271,5.07-5.07v-72.661c0-2.8-2.271-5.07-5.07-5.07h-14.658l-6.821-38.53 c-1.463-8.263-8.643-14.283-17.034-14.283h-20.904v-40.83c9.54,0,17.221-7.958,16.767-17.597 c-0.425-9.028-8.203-15.974-17.241-15.974h-82.472c-9.039,0-16.816,6.946-17.24,15.974c-0.454,9.639,7.227,17.597,16.766,17.597 v40.829h-0.705c-9.554,0-17.299,7.745-17.299,17.299v35.514H205.147V143.53c0-9.554-7.745-17.299-17.299-17.299h-0.705V85.401 h0.006c7.24,0,13.848-4.569,15.971-11.49c3.534-11.524-4.989-22.081-15.975-22.081h-82.951c-9.038,0-16.816,6.946-17.241,15.974 c-0.454,9.639,7.227,17.597,16.767,17.597v40.829H82.815c-8.391,0-15.571,6.022-17.035,14.283l-6.821,38.53H44.134 c-2.8,0-5.07,2.271-5.07,5.07v72.494c0,2.893,2.344,5.238,5.238,5.238l-14.324,80.909h175.168v-80.909h33.906v35.838 c0,9.27,7.516,16.786,16.786,16.786c9.27,0,16.786-7.515,16.786-16.786v-35.838h34.37v80.91H482.16z"/> </g> </g> <g> <g> <path d="M210.939,376.522H18.464C8.266,376.522,0,384.788,0,394.986v46.72c0,10.198,8.266,18.464,18.464,18.464h192.475 c10.198,0,18.464-8.266,18.464-18.464v-46.72C229.403,384.788,221.137,376.522,210.939,376.522z"/> </g> </g> <g> <g> <path d="M493.536,376.522H301.061c-10.198,0-18.464,8.266-18.464,18.464v46.72c0,10.198,8.266,18.464,18.464,18.464h192.475 c10.198,0,18.464-8.266,18.464-18.464v-46.72C512,384.788,503.734,376.522,493.536,376.522z"/> </g> </g> </svg>',
    marshalSvg: '<svg height="800px" width="800px" version="1.1" id="_x32_" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512" xml:space="preserve"><g> <path class="st0" d="M426.238,411.506c-10.256-15.346-25.252-24.568-40.025-30.778c-21.017-12.249-42.232-18.46-46.192-23.079 c-19.333-22.548,16.111-30.607,24.165-20.94c2.917,3.506,15.907,23.421,22.557,27.39c11.728,6.98,15.505,0.103,11.279-4.832 c-9.666-11.283-25.777-46.723-25.777-46.723l-47.779-7.468c3.404-4.859,6.697-10.479,9.593-16.903 c4.666-6.963,8.546-14.662,11.74-22.694c0.102-0.068,0.214-0.111,0.317-0.18c4.525-3.122,8.361-7.656,11.616-13.823 c3.272-6.193,6.172-14.114,9.268-24.944c1.57-5.492,2.292-10.264,2.292-14.508c0.004-4.902-1-9.145-2.852-12.6 c-1.578-2.969-3.726-5.132-5.954-6.732c0.33-5.433,0.475-10.026,0.521-13.456c29.688-2.574,45.107-9.564,51.3-27.792 c16.736-49.255-35.444-64.448-51.555-83.78C344.64,48.331,332.224,0,257.645,0c-74.601,0-86.996,48.331-103.107,67.663 c-16.112,19.332-65.572,33.652-51.552,83.78c5.098,18.228,20.243,24.439,47.022,27.356c0.046,3.644,0.188,8.657,0.573,14.713 c-1.869,1.54-3.678,3.387-5.017,5.92c-1.852,3.447-2.866,7.698-2.857,12.592c0.004,4.243,0.732,9.016,2.297,14.508 c4.14,14.431,7.878,23.738,12.72,30.573c2.1,2.96,4.491,5.303,7.04,7.254c3.884,9.991,8.798,19.486,14.97,27.741 c2.399,4.764,5.017,8.973,7.682,12.788l-48.99,7.657c0,0-16.108,35.44-25.774,46.723c-4.23,4.935-0.453,11.813,11.274,4.832 c6.655-3.969,19.645-23.883,22.557-27.39c8.054-9.667,43.498-1.608,24.166,20.94c-4.08,4.764-26.496,11.223-48.13,24.243 c-8.187,3.712-16.3,8.426-23.588,14.662c-7.352,6.313-13.807,14.251-18.344,24.105c-4.543,9.846-7.147,21.557-7.143,35.244 c0,3.182,0.137,6.467,0.428,9.871c0.21,2.378,1.112,4.312,2.177,5.92c2.028,2.96,4.714,5.184,8.08,7.451 c5.898,3.901,14.067,7.708,24.525,11.454c31.304,11.172,83.129,21.385,147.35,21.403c52.176,0,96.216-6.776,127.649-15.278 c15.727-4.268,28.284-8.939,37.356-13.601c4.546-2.344,8.22-4.662,11.133-7.203c1.462-1.282,2.738-2.634,3.815-4.226 c1.056-1.608,1.972-3.541,2.177-5.92c0.283-3.404,0.424-6.681,0.424-9.846C438.582,437.681,433.89,422.968,426.238,411.506z M177.582,91.829c0-7.998,6.497-14.5,14.499-14.5c8.007,0,14.5,6.501,14.5,14.5c0,4.859-2.408,9.127-6.078,11.771l10.508,23.387 l-7.386-0.633l-4.431,5.945l-7.113-15.816l-7.104,15.816l-4.432-5.945l-7.387,0.633l10.509-23.387 C179.998,100.973,177.582,96.688,177.582,91.829z M184.571,262.022l-0.719-4.063l-3.879-1.386 c-2.464-0.872-4.346-1.779-5.988-2.908c-2.426-1.711-4.62-4.055-7.19-8.836c-2.537-4.756-5.222-11.865-8.161-22.19 c-1.291-4.508-1.75-8.015-1.75-10.616c0.004-3.028,0.586-4.79,1.176-5.902c0.894-1.626,1.99-2.328,3.388-2.883 c0.949-0.368,1.95-0.506,2.528-0.548l4.897,1.034c7.788,5.894,13.374,18.597,13.374,18.597l4.191-41.916 c1.194,0.018,2.314,0.034,3.542,0.034h134.604l4.192,41.881c0,0,5.945-13.533,14.135-19.127l4.825-0.514 c0.56,0,2.69,0.239,4.123,1.198c0.813,0.522,1.472,1.129,2.079,2.242c0.595,1.112,1.168,2.874,1.181,5.902 c0,2.601-0.458,6.107-1.749,10.624c-3.91,13.772-7.412,21.778-10.629,26.218c-1.613,2.25-3.084,3.645-4.722,4.799 c-1.642,1.129-3.52,2.036-5.988,2.908l-3.878,1.386l-0.715,4.063c-4.538,25.397-17.63,39.691-27.296,50.461l-1.818,2.019v0.65 l-2.72,1.044l-0.176,0.068c-2.036,0.77-21.193,7.665-42.574,9.144c-11.352-0.795-22.108-3.079-29.991-5.192 c-3.829-1.026-6.964-2.002-9.183-2.738c0-0.094,0-0.162,0-0.256v-2.72l-1.818-2.019 C202.197,301.713,189.104,287.419,184.571,262.022z M301.074,356.862c-4.234,2.789-9.05,5.03-14.79,6.673 c-7.519,2.156-16.561,3.293-27.027,3.635v-29.409c14.965-1.634,27.955-5.227,35.098-7.519l3.969,9.264c0,2.686,0,5.234,0,7.528 C298.31,350.652,299.428,353.988,301.074,356.862z M246.366,337.761v29.409c-10.462-0.342-19.508-1.48-27.028-3.635 c-3.794-1.087-7.142-2.455-10.252-4.029c0.013-0.026,0.03-0.034,0.043-0.052c2.574-3.379,4.55-7.604,4.55-12.42 c0-4.525,0-9.829,0-16.039C221.14,333.261,232.962,336.306,246.366,337.761z M207.701,496.208c-5.334,0-9.666-4.328-9.666-9.666 c0-5.337,4.332-9.666,9.666-9.666c5.338,0,9.666,4.329,9.666,9.666C217.367,491.88,213.039,496.208,207.701,496.208z M207.701,452.702c-5.334,0-9.666-4.328-9.666-9.666c0-5.337,4.332-9.666,9.666-9.666c5.338,0,9.666,4.329,9.666,9.666 C217.367,448.374,213.039,452.702,207.701,452.702z M207.124,413.918l1.227-40.547c2.396,0.975,4.876,1.831,7.451,2.558 c9.003,2.566,19.195,3.789,30.564,4.132v0.154h6.445h6.445v-0.154c11.373-0.342,21.561-1.565,30.564-4.132 c4.44-1.258,8.542-2.951,12.429-4.902l0.21,6.81C280.356,385.963,232.744,404.123,207.124,413.918z"/> </g> </svg>',
    unknownSvg: '<svg height="800px" width="800px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512"  xml:space="preserve"> <g> <path class="st0" d="M396.138,85.295c-13.172-25.037-33.795-45.898-59.342-61.03C311.26,9.2,280.435,0.001,246.98,0.001 c-41.238-0.102-75.5,10.642-101.359,25.521c-25.962,14.826-37.156,32.088-37.156,32.088c-4.363,3.786-6.824,9.294-6.721,15.056 c0.118,5.77,2.775,11.186,7.273,14.784l35.933,28.78c7.324,5.864,17.806,5.644,24.875-0.518c0,0,4.414-7.978,18.247-15.88 c13.91-7.85,31.945-14.173,58.908-14.258c23.517-0.051,44.022,8.725,58.016,20.717c6.952,5.941,12.145,12.594,15.328,18.68 c3.208,6.136,4.379,11.5,4.363,15.574c-0.068,13.766-2.742,22.77-6.603,30.442c-2.945,5.729-6.789,10.813-11.738,15.744 c-7.384,7.384-17.398,14.207-28.634,20.479c-11.245,6.348-23.365,11.932-35.612,18.68c-13.978,7.74-28.77,18.858-39.701,35.544 c-5.449,8.249-9.71,17.686-12.416,27.641c-2.742,9.964-3.98,20.412-3.98,31.071c0,11.372,0,20.708,0,20.708 c0,10.719,8.69,19.41,19.41,19.41h46.762c10.719,0,19.41-8.691,19.41-19.41c0,0,0-9.336,0-20.708c0-4.107,0.467-6.755,0.917-8.436 c0.773-2.512,1.206-3.14,2.47-4.668c1.29-1.452,3.895-3.674,8.698-6.331c7.019-3.946,18.298-9.276,31.07-16.176 c19.121-10.456,42.367-24.646,61.972-48.062c9.752-11.686,18.374-25.758,24.323-41.968c6.001-16.21,9.242-34.431,9.226-53.96 C410.243,120.761,404.879,101.971,396.138,85.295z"/> <path class="st0" d="M228.809,406.44c-29.152,0-52.788,23.644-52.788,52.788c0,29.136,23.637,52.772,52.788,52.772 c29.136,0,52.763-23.636,52.763-52.772C281.572,430.084,257.945,406.44,228.809,406.44z"/> </g> </svg>'
}

class BoardRsc{
    public dotSvg = defaultBoardRsc.dotSvg;
    public attackDotSvg = defaultBoardRsc.attackDotSvg;
    public soldierSvg = defaultBoardRsc.soldierSvg;
    public spySvg = defaultBoardRsc.spySvg;
    public flagSvg = defaultBoardRsc.flagSvg;
    public bombSvg = defaultBoardRsc.bombSvg;
    public minerSvg = defaultBoardRsc.minerSvg;
    public scoutSvg = defaultBoardRsc.scoutSvg;
    public marshalSvg = defaultBoardRsc.marshalSvg;
    public unknownSvg = defaultBoardRsc.unknownSvg;
}

class RendererParams {
        public sq_width = 100;
        public sq_heigth= 100;
        public content_width = 80;
        public content_heigth = 80;
        public dot_width = 20;
        public dot_heigth = 20;
        public rank_width = 10;
        public rank_heigth = 10;
}

class BoardSvgRenderer{
    public state = new BoardState();
    public svgResources : BoardRsc;
    public readonly lakes = [42, 43, 46, 47, 52, 53, 56, 57];
    public renderParams = new RendererParams();

    constructor(svgResources : BoardRsc){
        this.svgResources = svgResources;
    }

    set_state(state: BoardState){
        this.state = state;
    }

    set_resources(svgResources: BoardRsc){
        this.svgResources = svgResources;
    }

    set_render_params(params: RendererParams){
        this.renderParams = params; 
    }

    _string_to_dom_element(str: string) : Element{
        let wrapper = document.createElement('div');
        wrapper.innerHTML = str;
        return wrapper.firstChild!;
    }

    create_a_placeholder_square_texture(index : number, highlight : boolean){
        let color = "lime"
        if (this.lakes.includes(index))
            color = "blue"
        else if (( (index%10) + Math.floor(index/10))%2 == 1)
            color = "green";
         else
            color = "lime";
        
        if (highlight == true){
            color = "yellow";
        }
        
        let result = "<svg><rect stroke-width=\"0\" width=\"100\" height=\"100\" stroke=\"gray\" fill=\""+ color +"\"/></svg>";
        return result;
    }

    set_attribute_recursive(element : any, atr : string, value : string){
        if (typeof element.setAttribute != 'function')
            return;
        element.setAttribute(atr, value);
        for(let i = 0; i<element.childNodes.length; ++i) 
            this.set_attribute_recursive(element.childNodes[i], atr, value)
    }

    _centered_square_content_from_string(content_string : string){
        let contentSvg = this._string_to_dom_element(content_string);
        contentSvg.setAttribute("width", this.renderParams.content_width + "px");
        contentSvg.setAttribute("height", this.renderParams.content_heigth + "px");
        contentSvg.setAttribute("x", ""+ (this.renderParams.sq_width - this.renderParams.content_width)/2);
        contentSvg.setAttribute("y", ""+ (this.renderParams.sq_heigth - this.renderParams.content_heigth)/2);
        return contentSvg;
    }

    _get_soldier_strength(piece_type: PieceType){
       let rank = 0;
       switch(piece_type) {
            case PieceType.SERGEANT: rank = 4; break; 
            case PieceType.LIEUTENANT: rank = 5; break;
            case PieceType.CAPTAIN: rank = 6; break;
            case PieceType.MAJOR: rank = 7; break;
            case PieceType.COLONEL: rank = 8; break;
            case PieceType.GENERAL: rank = 9; break;
        }
        return rank;
    }
    _render_soldier_rank(rank: number){
            let rankNode = document.createElementNS("http://www.w3.org/2000/svg", "text");
            rankNode.textContent = "" + rank;
            rankNode.setAttribute("y",""+ (0.35*this.renderParams.sq_heigth));
            rankNode.setAttribute("x", ""+ (this.renderParams.sq_width - this.renderParams.rank_width)/2);
            rankNode.setAttribute("width",""+ this.renderParams.rank_width);
            rankNode.setAttribute("heigth",""+ this.renderParams.rank_heigth);
            return rankNode;
    }
    render_piece(piece_type: PieceType, color: Color){
        let contentSvg : null | string | Element = null;
        let result = new Array(0);
        switch (piece_type){
            case PieceType.FLAG:
                contentSvg = this.svgResources.flagSvg;
                break;
            case PieceType.BOMB:
                contentSvg = this.svgResources.bombSvg;
                break;
            case PieceType.SPY:
                contentSvg = this.svgResources.spySvg;
                break;
            case PieceType.MINER:
                contentSvg = this.svgResources.minerSvg;
                break;
            case PieceType.SCOUT:
                contentSvg = this.svgResources.scoutSvg;
                break;
            case PieceType.MARSHAL:
                contentSvg = this.svgResources.marshalSvg;
                break;
            case PieceType.UNKNOWN:
                contentSvg = this.svgResources.unknownSvg;
                break;
            default:
                contentSvg = this.svgResources.soldierSvg;
                break;
        }
        
        contentSvg = this._centered_square_content_from_string(contentSvg);
       
        if (typeof color != "undefined"){
            let color_fill = "#000000";
            if (color == Color.RED)
                color_fill = "#AA0000";
            if (color == Color.BLUE)
                color_fill = "#0000ff";
        
            this.set_attribute_recursive(contentSvg,"fill", color_fill); 
        } else{
            this.set_attribute_recursive(contentSvg,"fill", "#000000"); 
        }

        
        result.push(contentSvg);

        let rank = this._get_soldier_strength(piece_type);
        if (rank != null && rank !=  0){
            result.push(this._render_soldier_rank(rank));
        }

        return result;
    }
    render_square(index: number){
        /*
            TODO:
            1. This method had have expanded to a slightly above reasonable size, refactor it
            2. The renderer should also export abbility to render items based on piece type, so can use it in unit selector 
        */
        let result = document.createElementNS("http://www.w3.org/2000/svg","svg");
        result.setAttribute("id", "square" + index);
        const square = this.state.squares[index];
        
        let square_svg : string | Element;

        if (square.highlight){
            square_svg = (typeof this.svgResources.highlightedSquaresSvg == "undefined") ? this.create_a_placeholder_square_texture(index, true): this.svgResources.highlightedSquaresSvg[index];
        } else{
            square_svg = (typeof this.svgResources.squaresSvg == "undefined") ? this.create_a_placeholder_square_texture(index, false): this.svgResources.squaresSvg[index];
        }

        square_svg = (typeof square_svg == "string")?this._string_to_dom_element(square_svg):square_svg;
        square_svg.setAttribute("width", this.renderParams.sq_width + "px");
        square_svg.setAttribute("height", this.renderParams.sq_heigth + "px");
        result.append(square_svg);

        if (square.piece != null){
            let nodes = this.render_piece(square.piece.type, square.piece.color);
            for(let i = 0; i<nodes.length; ++i)
                result.append(nodes[i]);
        }

        result.setAttribute("id", "sq_" + index);
        result.setAttribute("fill", "white"); // for rank rendering
        return result;
    }

};


class BoardView{
        public squares_svgs : Array<any>  = new Array(100);
        private __board_svg_grid: null | any = null; // set by _create_game_grid
        private __sq_svgs: null | any = null
        public svgResources : BoardRsc = defaultBoardRsc;
        public renderer = new BoardSvgRenderer(this.svgResources);
        public model : null | BoardModel;
        public controller : any; // TODO: replace it with boardViewController interface
        public board_width = 1000;
        public board_height = 1000;
        public boardElement : any;

    constructor(){
        this.svgResources = defaultBoardRsc;
        this.model = null;
        this.controller = null;

        this.set_controller(null); // this doesn't set field "controller" to null but to controller that do nothing
        this.set_model(null); //  this doesn't set field "model" to null but to model that is not reactive in any way
        this.boardElement = this._create_game_grid(); // initializes board element and its parts
        this.refresh();
    };

    _create_game_grid(){
        let wrapper = document.createElement("div");
        wrapper.setAttribute("id", "BoardGrid");

        this.__board_svg_grid = document.createElementNS("http://www.w3.org/2000/svg","svg");
        this.__board_svg_grid.setAttribute("viewBox", "0 0 1000 1000");
        this.__board_svg_grid.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        
        wrapper.append(this.__board_svg_grid);

        for (let i = 0; i<10; ++i)
            for (let j = 0; j<10; ++j){
            let index = 10*i + j;
            let sq_svg = this.renderer.render_square(index);
            this.__sq_svgs[index] = sq_svg;
            this.__board_svg_grid.append(sq_svg);
        }
        
        return wrapper;
    }

    __pass_click_event_to_controller(index : number){
        this.controller.handle_sq_click(index);
    }

    __pass_mouse_enter_event_to_controller(index: number){
        if ((typeof this.controller.handle_mouse_enter) != "undefined")
            this.controller.handle_mouse_enter(index); 
    }

    __pass_mouse_leave_event_to_controller(index : number){
        if ((typeof this.controller.handle_mouse_leave) != "undefined" )
            this.controller.handle_mouse_leave(index); 
    }

    set_model(model: BoardModel | null | undefined){
        if (model == null){ // TODO: check if syntax is correct
            this.model = new BoardModel(new MoveGenerator(),new BoardState())
        } else{
            this.model = model;
        }
    }

    set_controller(controller){
        if (controller == null){ // TODO: make the controller be able to handle any event of given square
            this.controller = {
                                handle_sq_click(index){}
                              }
        } else{
            this.controller = controller;
        }
    }

    set_state(boardstate: BoardState){
        this.renderer.set_state(boardstate);
        this.refresh();
        return this.boardElement;
    }

    set_size(size: number){
        const ratio = size / this.board_width;
        this.board_width = Math.floor(this.board_width * ratio);
        this.board_height = Math.floor(this.board_height * ratio);
        this.refresh();
    }

    set_resources(rsc: BoardRsc){
        let state = this.renderer.state;
        this.renderer = new BoardSvgRenderer(rsc);
        this.renderer.set_state(state);
        this.refresh();
    }

    refresh(){
         this.__board_svg_grid.setAttribute("width", this.board_width);
         this.__board_svg_grid.setAttribute("height", this.board_height);

        for (let i = 0; i<10; ++i)
            for (let j = 0; j<10; ++j){
            let index = 10*i + j;
            let sq_svg = this.renderer.render_square(index);
        
            sq_svg.setAttribute("x",  j * this.renderer.renderParams.sq_width +"px");
            sq_svg.setAttribute("y",  i * this.renderer.renderParams.sq_heigth + "px");
            sq_svg.onclick =  (ev => this.__pass_click_event_to_controller(index));
            sq_svg.onmouseenter = (ev => this.__pass_mouse_enter_event_to_controller(index));
            sq_svg.onmouseleave = (ev => this.__pass_mouse_leave_event_to_controller(index));


            this.__sq_svgs[index].replaceWith(sq_svg);
            this.__sq_svgs[index] = sq_svg;
        }
    }
};