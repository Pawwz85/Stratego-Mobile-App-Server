
const defaultBoardRsc = {
    dotSvg: '<svg height="800px" width="800px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 31.955 31.955" xml:space="preserve"> <g> <path style="fill:#030104;" d="M27.25,4.655C20.996-1.571,10.88-1.546,4.656,4.706C-1.571,10.96-1.548,21.076,4.705,27.3 c6.256,6.226,16.374,6.203,22.597-0.051C33.526,20.995,33.505,10.878,27.25,4.655z"/> <path style="fill:#030104;" d="M13.288,23.896l-1.768,5.207c2.567,0.829,5.331,0.886,7.926,0.17l-0.665-5.416 C17.01,24.487,15.067,24.5,13.288,23.896z M8.12,13.122l-5.645-0.859c-0.741,2.666-0.666,5.514,0.225,8.143l5.491-1.375 C7.452,17.138,7.426,15.029,8.12,13.122z M28.763,11.333l-4.965,1.675c0.798,2.106,0.716,4.468-0.247,6.522l5.351,0.672 C29.827,17.319,29.78,14.193,28.763,11.333z M11.394,2.883l1.018,5.528c2.027-0.954,4.356-1.05,6.442-0.288l1.583-5.137 C17.523,1.94,14.328,1.906,11.394,2.883z"/> <circle style="fill:#030104;" cx="15.979" cy="15.977" r="6.117"/> </g> </svg>',
    attackDotSvg: '<svg height="800px" width="800px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 31.955 31.955" xml:space="preserve"> <g> <path style="fill:#030104;" d="M27.25,4.655C20.996-1.571,10.88-1.546,4.656,4.706C-1.571,10.96-1.548,21.076,4.705,27.3 c6.256,6.226,16.374,6.203,22.597-0.051C33.526,20.995,33.505,10.878,27.25,4.655z"/> <path style="fill:#030104;" d="M13.288,23.896l-1.768,5.207c2.567,0.829,5.331,0.886,7.926,0.17l-0.665-5.416 C17.01,24.487,15.067,24.5,13.288,23.896z M8.12,13.122l-5.645-0.859c-0.741,2.666-0.666,5.514,0.225,8.143l5.491-1.375 C7.452,17.138,7.426,15.029,8.12,13.122z M28.763,11.333l-4.965,1.675c0.798,2.106,0.716,4.468-0.247,6.522l5.351,0.672 C29.827,17.319,29.78,14.193,28.763,11.333z M11.394,2.883l1.018,5.528c2.027-0.954,4.356-1.05,6.442-0.288l1.583-5.137 C17.523,1.94,14.328,1.906,11.394,2.883z"/> <circle style="fill:#030104;" cx="15.979" cy="15.977" r="6.117"/> </g> </svg>',
    soldierSvg: '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="800px" height="800px" viewBox="0 0 512 512"  xml:space="preserve"> <style type="text/css"> <![CDATA[ .st0{fill:#000000;} ]]> </style> <g> <path class="st0" d="M449.085,464.424c0,0-5.672-45.109-8.797-51.563c-2.813-5.75-92.75-50.375-112.063-61.563l-0.578,0.203 v-25.609c7.203-7.656,13.859-17.016,19.281-28.563c1.141-2.438,1.938-5.047,2.703-7.906c1.141-4.266,2.094-8.922,2.781-12.578 c0.016-0.063,0.016-0.109,0.031-0.172c3.094-0.75,5.906-2.172,8.313-3.891c5.375-3.922,9.281-9.328,12.453-14.984 c3.141-5.672,5.484-11.656,7.031-16.953c1.172-4.047,1.75-7.688,1.766-11.078c0-3.641-0.719-7.063-2.219-9.969 c-1.125-2.188-2.672-4.031-4.344-5.438c-0.203-0.156-0.406-0.266-0.594-0.422l-0.781-31.438 c7.531-6.422,10.313-14.719,10.313-20.484c0-7.453,0-18.078,0-29.781c0-15.938-11.25-21.281-20.984-23.359 c1,2.609,1.5,5.359,1.5,8.078c0,3.203-0.688,6.422-2.047,9.422c-7.266-14.047-49.781-96.188-57.719-110.359 c-10.188-18.219-41.734-23.531-56.609-1.922c-15.844,23.016-33.953,53.688-36.234,61.375l12.172-48.344 c-13.078-6.203-30.5-1.922-34.813,9.016c-3.25,8.297-33.891,79.75-39.391,92.563c-0.031-0.031-0.063-0.063-0.078-0.109 c-1.703-3.297-2.578-6.891-2.578-10.5c0-2.75,0.516-5.5,1.516-8.141v-0.016c0,0,0.172-0.391,0.453-1.141 c-9.828,2-21.359,7.281-21.359,23.438c0,11.703,0,22.328,0,29.781c0,5.781,2.797,14.094,10.344,20.516l-0.781,31.422 c-1.625,1.25-3.156,2.813-4.328,4.781c-1.891,3.125-2.844,6.938-2.828,11.031c0,3.391,0.609,7.031,1.781,11.078 c2.078,7.078,5.484,15.344,10.469,22.484c2.5,3.547,5.406,6.844,9.016,9.453c2.391,1.719,5.203,3.141,8.313,3.891 c0.234,1.266,0.5,2.656,0.813,4.109c0.563,2.781,1.234,5.797,2,8.641c0.781,2.859,1.563,5.469,2.703,7.906 c5.25,11.188,11.688,20.313,18.641,27.844v26.328l-0.578-0.203c-19.313,11.188-109.25,55.813-112.047,61.563 c-3.141,6.453-8.813,51.563-8.813,51.563c-1.484,7.422,0.25,15.141,4.766,21.203c4.531,6.078,11.406,9.953,18.953,10.656 c0,0,42.672,15.719,169.375,15.719c126.688,0,169.359-15.719,169.359-15.719c7.547-0.703,14.438-4.578,18.953-10.656 C448.851,479.564,450.569,471.846,449.085,464.424z M98.866,425.955l-6.75-12.531l59.078-30.829l7.703,12.844L98.866,425.955z M256.007,485.33c-5.75,0-10.422-4.656-10.422-10.406s4.672-10.406,10.422-10.406s10.406,4.656,10.406,10.406 S261.757,485.33,256.007,485.33z M256.007,421.768c-5.75,0-10.422-4.656-10.422-10.422c0-5.75,4.672-10.407,10.422-10.407 s10.406,4.656,10.406,10.407C266.413,417.111,261.757,421.768,256.007,421.768z M278.866,338.361 c-10.453,3.266-19.188,3.844-22.547,3.844c-2.234,0-6.891-0.25-12.813-1.391c-8.906-1.719-20.672-5.422-32.219-13.063 c-11.547-7.656-22.906-19.172-31.375-37.109c-0.406-0.813-1.109-2.906-1.75-5.281c-0.953-3.609-1.875-8-2.5-11.438 c-0.344-1.703-0.594-3.188-0.781-4.25c-0.078-0.516-0.156-0.922-0.203-1.219l-0.063-0.406l-1.219-7.688l-7.688,1.156l-0.703,0.047 c-1.078,0-2.281-0.344-3.969-1.547c-2.484-1.734-5.469-5.438-7.891-9.844c-2.453-4.406-4.453-9.484-5.672-13.719 c-0.859-2.953-1.141-5.188-1.141-6.688c0-1.641,0.297-2.406,0.469-2.781l0.438-0.547c0.266-0.219,0.781-0.5,1.625-0.719 c0.813-0.203,1.875-0.313,2.813-0.313c0.75,0,1.406,0.063,1.844,0.109l0.469,0.063l8.688,1.734 c0.172,0.328,0.344,0.609,0.516,0.953c0.016-0.266,0.063-0.547,0.094-0.828l0.094,0.016v-0.891c0.859-8.047,2.391-21.031,3.703-32 c28.766,8.641,74.672,20.5,74.672,20.5c9.469,2.844,19.625,2.844,29.078,0c0,0,45.953-11.859,74.719-20.516 c1.313,10.984,2.828,23.969,3.703,32.016v0.891l0.109-0.016c0.016,0.281,0.047,0.563,0.063,0.828 c0.188-0.328,0.359-0.625,0.516-0.938l8.719-1.75l0,0c0.234-0.031,1.188-0.172,2.281-0.172c0.844,0,1.766,0.078,2.531,0.25 c0.578,0.125,1.063,0.297,1.391,0.469c0.531,0.266,0.672,0.422,0.875,0.734c0.188,0.328,0.547,1.047,0.563,2.906 c0,1.5-0.281,3.734-1.141,6.688c-1.625,5.656-4.656,12.766-8.25,17.844c-1.781,2.547-3.688,4.547-5.328,5.719 c-1.688,1.203-2.891,1.547-3.953,1.547l-0.703-0.047l-7.703-1.156l-1.219,7.688l-0.031,0.172 c-0.141,0.953-0.875,5.453-1.922,10.375c-0.531,2.453-1.109,5.016-1.719,7.219c-0.578,2.172-1.25,4.078-1.609,4.828 c-5.656,11.969-12.594,21.047-20.016,28.063C301.616,329.22,289.366,335.095,278.866,338.361z M370.929,466.658h-13.984h-5.344 v5.344v13.984l-7-6.578l-7,6.578v-13.984v-5.344h-5.344h-13.969l6.578-7l-6.578-6.984h13.969h5.344v-5.359v-13.969l7,6.563l7-6.563 v13.969v5.359h5.344h13.984l-6.578,6.984L370.929,466.658z M413.147,425.955l-60.031-30.516l7.703-12.844l59.078,30.829 L413.147,425.955z"/> </g> </svg>',
    spySvg: '<svg width="800px" height="800px" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="#000000" d="M218 19c-1 0-2.76.52-5.502 3.107-2.742 2.589-6.006 7.021-9.191 12.76-6.37 11.478-12.527 28.033-17.666 45.653-4.33 14.844-7.91 30.457-10.616 44.601 54.351 24.019 107.599 24.019 161.95 0-2.706-14.144-6.286-29.757-10.616-44.601-5.139-17.62-11.295-34.175-17.666-45.653-3.185-5.739-6.45-10.171-9.191-12.76C296.76 19.52 295 19 294 19c-6.5 0-9.092 1.375-10.822 2.85-1.73 1.474-3.02 3.81-4.358 7.34-1.338 3.53-2.397 8.024-5.55 12.783C270.116 46.73 263.367 51 256 51c-7.433 0-14.24-4.195-17.455-8.988-3.214-4.794-4.26-9.335-5.576-12.881-1.316-3.546-2.575-5.867-4.254-7.315C227.035 20.37 224.5 19 218 19zm-46.111 124.334c-1.41 9.278-2.296 17.16-2.57 22.602 6.61 5.087 17.736 10.007 31.742 13.302C217.18 183.031 236.6 185 256 185s38.82-1.969 54.94-5.762c14.005-3.295 25.13-8.215 31.742-13.302-.275-5.443-1.161-13.324-2.57-22.602-55.757 23.332-112.467 23.332-168.223 0zM151.945 155.1c-19.206 3.36-36.706 7.385-51.918 11.63-19.879 5.548-35.905 11.489-46.545 16.57-5.32 2.542-9.312 4.915-11.494 6.57-.37.28-.247.306-.445.546.333.677.82 1.456 1.73 2.479 1.973 2.216 5.564 4.992 10.627 7.744 10.127 5.504 25.944 10.958 45.725 15.506C139.187 225.24 194.703 231 256 231s116.813-5.76 156.375-14.855c19.78-4.548 35.598-10.002 45.725-15.506 5.063-2.752 8.653-5.528 10.627-7.744.91-1.023 1.397-1.802 1.73-2.479-.198-.24-.075-.266-.445-.547-2.182-1.654-6.174-4.027-11.494-6.568-10.64-5.082-26.666-11.023-46.545-16.57-15.212-4.246-32.712-8.272-51.918-11.631.608 5.787.945 10.866.945 14.9v3.729l-2.637 2.634c-10.121 10.122-25.422 16.191-43.302 20.399C297.18 200.969 276.6 203 256 203s-41.18-2.031-59.06-6.238c-17.881-4.208-33.182-10.277-43.303-20.399L151 173.73V170c0-4.034.337-9.113.945-14.9zm1.094 88.205C154.558 308.17 200.64 359 256 359c55.36 0 101.442-50.83 102.96-115.695a748.452 748.452 0 0 1-19.284 2.013c-1.33 5.252-6.884 25.248-15.676 30.682-13.61 8.412-34.006 7.756-48 0-7.986-4.426-14.865-19.196-18.064-27.012-.648.002-1.287.012-1.936.012-.65 0-1.288-.01-1.936-.012-3.2 7.816-10.078 22.586-18.064 27.012-13.994 7.756-34.39 8.412-48 0-8.792-5.434-14.346-25.43-15.676-30.682a748.452 748.452 0 0 1-19.285-2.013zM137.4 267.209c-47.432 13.23-77.243 32.253-113.546 61.082 42.575 4.442 67.486 21.318 101.265 48.719l16.928 13.732-21.686 2.211c-13.663 1.393-28.446 8.622-39.3 17.3-5.925 4.738-10.178 10.06-12.957 14.356 44.68 5.864 73.463 10.086 98.011 20.147 18.603 7.624 34.81 18.89 53.737 35.781l5.304-23.576c-1.838-9.734-4.134-19.884-6.879-30.3-5.12-7.23-9.698-14.866-13.136-22.007C201.612 397.326 199 391 199 384c0-3.283.936-6.396 2.428-9.133a480.414 480.414 0 0 0-6.942-16.863c-29.083-19.498-50.217-52.359-57.086-90.795zm237.2 0c-6.87 38.436-28.003 71.297-57.086 90.795a480.521 480.521 0 0 0-6.942 16.861c1.493 2.737 2.428 5.851 2.428 9.135 0 7-2.612 13.326-6.14 20.654-3.44 7.142-8.019 14.78-13.14 22.01-2.778 10.547-5.099 20.82-6.949 30.666l5.14 23.42c19.03-17.01 35.293-28.338 53.974-35.994 24.548-10.06 53.33-14.283 98.011-20.147-2.78-4.297-7.032-9.618-12.957-14.355-10.854-8.679-25.637-15.908-39.3-17.3l-21.686-2.212 16.928-13.732c33.779-27.4 58.69-44.277 101.265-48.719-36.303-28.829-66.114-47.851-113.546-61.082zM256 377c-8 0-19.592.098-28.234 1.826-4.321.864-7.8 2.222-9.393 3.324-1.592 1.103-1.373.85-1.373 1.85s1.388 6.674 4.36 12.846c2.971 6.172 7.247 13.32 11.964 19.924 4.717 6.604 9.925 12.699 14.465 16.806 4.075 3.687 7.842 5.121 8.211 5.377.37-.256 4.136-1.69 8.21-5.377 4.54-4.107 9.749-10.202 14.466-16.806 4.717-6.605 8.993-13.752 11.965-19.924C293.612 390.674 295 385 295 384s.22-.747-1.373-1.85c-1.593-1.102-5.072-2.46-9.393-3.324C275.592 377.098 264 377 256 377zm0 61.953c-.042.03-.051.047 0 .047s.042-.018 0-.047zm-11.648 14.701L235.047 495h41.56l-9.058-41.285C264.162 455.71 260.449 457 256 457c-4.492 0-8.235-1.316-11.648-3.346z"/></svg>',
    flagSvg: '<svg fill="#000000" width="800px" height="800px" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg"> <title>flag</title> <path d="M0 30.016q0 0.832 0.576 1.408t1.44 0.576 1.408-0.576 0.576-1.408v-28q0-0.832-0.576-1.408t-1.408-0.608-1.44 0.608-0.576 1.408v28zM6.016 18.016h9.984v4h16l-4-8 4-8h-12v-4h-13.984v16zM10.016 14.016v-8h5.984v8h-5.984zM20 18.016v-8h5.536l-2.016 4 2.016 4h-5.536z"></path> </svg>',
    bombSvg: '<svg width="800px" height="800px" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--emojione-monotone" preserveAspectRatio="xMidYMid meet"><path d="M41.245 11.293c-.981.966-1.961 1.934-2.94 2.9c-.862.852.475 2.172 1.336 1.32c.981-.967 1.961-1.934 2.939-2.902c.865-.851-.475-2.171-1.335-1.318" fill="#000000"></path><path d="M46.761 8.486l2.91-2.873c.862-.852-.475-2.172-1.337-1.32l-2.911 2.873c-.864.854.473 2.173 1.338 1.32" fill="#000000"></path><path d="M48.334 15.514c.862.852 2.199-.469 1.337-1.32c-.981-.967-1.958-1.935-2.94-2.9c-.859-.853-2.199.467-1.337 1.318l2.94 2.902" fill="#000000"></path><path d="M41.215 8.486c.865.853 2.203-.467 1.34-1.318c-.971-.959-1.941-1.917-2.914-2.875c-.861-.853-2.198.469-1.336 1.32l2.91 2.873" fill="#000000"></path><path d="M44.934 16.904v-2.889c0-1.204-1.893-1.204-1.893 0v2.889c0 1.203 1.893 1.203 1.893 0" fill="#000000"></path><path d="M44.934 5.751V2.902c0-1.203-1.893-1.203-1.893 0v2.849c0 1.204 1.893 1.204 1.893 0" fill="#000000"></path><path d="M48.174 10.837h2.905c1.221 0 1.221-1.866 0-1.866h-2.905c-1.219 0-1.219 1.866 0 1.866" fill="#000000"></path><path d="M32.832 18.229A22.243 22.243 0 0 0 20.45 21.96l-3.778-3.731l-2.254 2.224c-2.295-2.496-4.403-5.648-3.122-7.889c2.564-4.49 16.702-4.402 28.327-1.748l.429-1.826C27.66 6.158 12.791 6.127 9.641 11.644c-1.509 2.64-.353 6.049 3.431 10.138l-2.409 2.377l3.779 3.73a21.604 21.604 0 0 0-3.779 12.226C10.663 52.2 20.589 62 32.832 62C45.078 62 55 52.2 55 40.114c0-12.088-9.922-21.885-22.168-21.885" fill="#000000"></path></svg>',
    unknownSvg: '<svg height="800px" width="800px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512"  xml:space="preserve"> <style type="text/css"> .st0{fill:#000000;} </style> <g> <path class="st0" d="M396.138,85.295c-13.172-25.037-33.795-45.898-59.342-61.03C311.26,9.2,280.435,0.001,246.98,0.001 c-41.238-0.102-75.5,10.642-101.359,25.521c-25.962,14.826-37.156,32.088-37.156,32.088c-4.363,3.786-6.824,9.294-6.721,15.056 c0.118,5.77,2.775,11.186,7.273,14.784l35.933,28.78c7.324,5.864,17.806,5.644,24.875-0.518c0,0,4.414-7.978,18.247-15.88 c13.91-7.85,31.945-14.173,58.908-14.258c23.517-0.051,44.022,8.725,58.016,20.717c6.952,5.941,12.145,12.594,15.328,18.68 c3.208,6.136,4.379,11.5,4.363,15.574c-0.068,13.766-2.742,22.77-6.603,30.442c-2.945,5.729-6.789,10.813-11.738,15.744 c-7.384,7.384-17.398,14.207-28.634,20.479c-11.245,6.348-23.365,11.932-35.612,18.68c-13.978,7.74-28.77,18.858-39.701,35.544 c-5.449,8.249-9.71,17.686-12.416,27.641c-2.742,9.964-3.98,20.412-3.98,31.071c0,11.372,0,20.708,0,20.708 c0,10.719,8.69,19.41,19.41,19.41h46.762c10.719,0,19.41-8.691,19.41-19.41c0,0,0-9.336,0-20.708c0-4.107,0.467-6.755,0.917-8.436 c0.773-2.512,1.206-3.14,2.47-4.668c1.29-1.452,3.895-3.674,8.698-6.331c7.019-3.946,18.298-9.276,31.07-16.176 c19.121-10.456,42.367-24.646,61.972-48.062c9.752-11.686,18.374-25.758,24.323-41.968c6.001-16.21,9.242-34.431,9.226-53.96 C410.243,120.761,404.879,101.971,396.138,85.295z"/> <path class="st0" d="M228.809,406.44c-29.152,0-52.788,23.644-52.788,52.788c0,29.136,23.637,52.772,52.788,52.772 c29.136,0,52.763-23.636,52.763-52.772C281.572,430.084,257.945,406.44,228.809,406.44z"/> </g> </svg>'
}

class RendererParams {
    constructor(){
        this.sq_width = 100;
        this.sq_heigth= 100;
        this.content_width = 80;
        this.content_heigth = 80;
        this.dot_width = 20;
        this.dot_heigth = 20;
    }
}

class BoardSvgRenderer{
    constructor(svgResources){
        this.state = new BoardState();
        this.svgResources = svgResources;
        this.lakes = [42, 43, 46, 47, 52, 53, 56, 57];
        this.renderParams = new RendererParams();
    }

    set_state(state){
        this.state = state;
    }

    set_resources(svgResources){
        this.svgResources = svgResources;
    }

    set_render_params(params){
        this.renderParams = params; 
    }

    _string_to_dom_element(str){
        let wrapper = document.createElement('div');
        wrapper.innerHTML = str;
        return wrapper.firstChild;
    }

    create_a_placeholder_square_texture(index, highlight){
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

    _centered_square_content_from_string(sq, content_string, content_heigth, content_width){
        let contentSvg = this._string_to_dom_element(contentSvg);
        contentSvg.setAttribute("width", this.renderParams.content_width + "px");
        contentSvg.setAttribute("height", this.renderParams.content_heigth + "px");
        contentSvg.setAttribute("x", (this.renderParams.sq_width - this.renderParams.content_width)/2);
        contentSvg.setAttribute("y", (this.renderParams.sq_heigth - this.renderParams.content_heigth)/2);
        return contentSvg;
    }

    _render_square_content(sq){
        let contentSvg = null;
        if (sq.piece != null){
            switch (sq.piece.type){
                case PieceTypes.FLAG:
                    contentSvg = this.svgResources.flagSvg;
                    break;
                case PieceTypes.BOMB:
                    contentSvg = this.svgResources.bombSvg;
                    break;
                case PieceTypes.SPY:
                    contentSvg = this.svgResources.spySvg;
                    break;
                case PieceTypes.UNKNOWN:
                    contentSvg = this.svgResources.unknownSvg;
                    break;
                default:
                    contentSvg = this.svgResources.soldierSvg;
                    break;
            }

            contentSvg = this._centered_square_content_from_string(sq, contentSvg, this.renderParams.content_heigth, this.renderParams.content_width);
        }
        return contentSvg;
    }

    render_square(index){
        let result = document.createElementNS("http://www.w3.org/2000/svg","svg");
        result.setAttribute("id", "square" + index);
        result.setAttribute("viewBox", "0 0 "+ this.renderParams.sq_width +" " + this.renderParams.sq_heigth);
        const square = this.state.squares[index];
        
        let square_svg = "";

        if (square.highlight){
            square_svg = (typeof this.svgResources.highlightedSquaresSvg == "undefined") ? this.create_a_placeholder_square_texture(index, true): this.svgResources.highlightedSquaresSvg[index];
        } else{
            square_svg = (typeof this.svgResources.squaresSvg == "undefined") ? this.create_a_placeholder_square_texture(index, false): this.svgResources.squaresSvg[index];
        }

        square_svg = this._string_to_dom_element(square_svg);
        square_svg.setAttribute("width", this.renderParams.sq_width + "px");
        square_svg.setAttribute("height", this.renderParams.sq_heigth + "px");
        result.append(square_svg);

        let content_svg = this._render_square_content(square);
        if(content_svg != null){
            result.append(content_svg);
        }

        if (square.draw_dot){
            let dot_svg = (square.piece == null) ? this.svgResources.dotSvg : this.svgResources.attackDotSvg;
            result.append(this._centered_square_content_from_string(dot_svg, this.renderParams.dot_heigth, this.renderParams.dot_width));
        }
        result.setAttribute("id", "sq_" + index);
        return result;
    }
};

// TODO: implement
class BoardView{

    constructor(){
        this.squares_svgs = new Array(100);
        this.svgResources = defaultBoardRsc;
        this.renderer = new BoardSvgRenderer(this.svgResources);
        this.model = null;
        this.controller = null;
        this.boardElement = this._create_game_grid();

        this.board_width = 1000;
        this.board_height = 1000;

        this.set_controller(null); // this doesn't set field "controller" to null but to controller that do nothing
        this.set_model(null); //  this doesn't set field "model" to null but to model that is not reactive in any way

    };

    _create_game_grid(){
        let wrapper = document.createElement("div");
        wrapper.setAttribute("id", "BoardGrid");

        let board_svg_grid = document.createElementNS("http://www.w3.org/2000/svg","svg");
        board_svg_grid.setAttribute("viewBox", "0 0 1000 1000");
        board_svg_grid.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        board_svg_grid.setAttributeNode
        wrapper.append(board_svg_grid);
        
        this.board_width = 10 * this.renderer.renderParams.sq_width;
        this.board_height = 10 * this.renderer.renderParams.sq_heigth;

        board_svg_grid.setAttribute("width", this.board_width);
        board_svg_grid.setAttribute("height", this.board_height);

        for (let i = 0; i<10; ++i)
            for (let j = 0; j<10; ++j){
            let index = 10*i + j;
            let sq_svg = this.renderer.render_square(index);
            // sq_svg.onclick = // Todo: invoke a method and report click to controller 
            sq_svg.setAttribute("x",  j *this.renderer.renderParams.sq_width +"px");
            sq_svg.setAttribute("y",  i * this.renderer.renderParams.sq_heigth + "px");

            sq_svg.onclick =  (ev => this.__pass_click_event_to_controller(index));
            board_svg_grid.append(sq_svg);
        }
        
        return wrapper;
    }

    __pass_click_event_to_controller(index){
        this.controller.handle_sq_click(index)
    }

    set_model(model){
        if (model == null){ // TODO: check if syntax is correct
            this.model = {
                            execute_move(move){return false;},
                            set_selected_square_id(id){}
                         }
        } else{
            this.model = model;
        }
    }

    set_controller(controller){
        if (controller == null){ // TODO: check if syntax is correct
            this.controller = {
                                handle_sq_click(index){}
                              }
        } else{
            this.controller = controller;
        }
    }

    set_state(boardstate){
        this.renderer.set_state(boardstate);
        let new_view = this._create_game_grid();
        this.boardElement.innerHTML = new_view.innerHTML;
        return this.boardElement;
    }

};